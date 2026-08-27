---
name: hermes-messaging-delivery
description: "排查 Hermes cron 投递/主动推送失败：独立 webhook 未配置、出站投递配置。"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [hermes, dingtalk, cron, delivery, webhook, gateway, messaging]
    related_skills: [hermes-agent, hermes-admin, webhook-subscriptions]
---

# Hermes Messaging Delivery (消息平台出站投递)

配置和排查 Hermes 消息平台（DingTalk 钉钉、Yuanbao 元宝等）的**出站投递**问题，尤其是 cron 定时任务/`hermes send` 的主动推送失败。

## 核心模型：两条发送路径（必须先讲清楚）

Hermes 平台插件有**两条完全不同的发送路径**，配置要求不同：

| 路径 | 触发场景 | 机制 | 需要配置吗 |
|:-----|:---------|:-----|:----------|
| **回复路径 (reply)** | 用户发消息 → agent 回复 | 每条入站消息自带临时 `session_webhook`（DingTalk）/ 会话凭证，插件缓存 `chat_id -> (webhook, expiry)`，用它回 | ❌ 免费，无需额外配置 |
| **主动投递路径 (out-of-process / proactive)** | cron 定时任务投递、`hermes send`、跨平台转发 | 没有入站消息可依附，必须用**静态机器人 webhook**（或平台 bot token） | ✅ **必须配置** |

**典型症状**：聊天回复一切正常，但 cron 任务/主动推送报错。用户常看到的错误等价于：

```
cron.scheduler: delivery error: DingTalk not configured.
Set DINGTALK_WEBHOOK_URL env var or webhook_url in dingtalk platform extra config.
```

中文语境可能被转述为「XX账号的独立 webhook 未配置」——本质就是**主动投递路径缺静态 webhook**，不是插件坏了。

## 排查工作流（按序执行）

1. **看 gateway 日志的错误签名**：
   ```bash
   grep -i "delivery error\|No valid session_webhook\|not configured" ~/.hermes/logs/gateway.log | tail
   ```
   - `delivery error: <Platform> not configured` → 主动投递路径缺配置
   - `No valid session_webhook for chat_id=...` → 回复路径 webhook 过期/缓存被清（正常限制：每条入站消息才刷新）

2. **对时间戳找 cron 投递产物**：错误签名的时间戳 与 `~/.hermes/cron/output/<job_id>/<timestamp>.md` 对齐，确认是哪个 job、投递目标是谁。cron 输出文件头部会标 `(FAILED)` 和 Schedule。

3. **查插件源码确认配置项**：`grep -rn "WEBHOOK_URL\|webhook_url\|standalone_sender" /usr/local/lib/hermes-agent/plugins/platforms/<platform>/`（adapter.py 的 `standalone_sender_fn` 是出站投递的实现）。`plugin.yaml` 的 `optional_env:` 列出合法配置项。

4. **查环境变量**：`grep -i "<PLATFORM>" ~/.hermes/.env | sed 's/=.*/=<REDACTED>/'`，确认缺哪个变量。

## 修复步骤（DingTalk 实例）

1. 钉钉：群设置 → 机器人 → 添加机器人 → **自定义（Webhook 接入）**，复制 `https://oapi.dingtalk.com/robot/send?access_token=xxx`
2. **安全设置选「自定义关键词」**（如 `Hermes`）——⚠️ 不要选「加签」，Hermes 发送端未实现 HMAC 签名，加签必失败
3. 配置（二选一）：
   ```bash
   # 环境变量（推荐，插件 optional_env）
   echo 'DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=你的token' >> ~/.hermes/.env
   # 或 config.yaml 的 dingtalk platform extra
   hermes config set gateway.platforms.dingtalk.webhook_url "https://oapi.dingtalk.com/robot/send?access_token=你的token"
   ```
4. `hermes gateway restart` 生效
5. 验证：`hermes send --to dingtalk "Hermes 测试消息"` 或手动触发一个 cron job

## 平台速查

| 平台 | 主动投递配置 | 备注 |
|:-----|:-------------|:-----|
| DingTalk | `DINGTALK_WEBHOOK_URL` / `webhook_url` | 群机器人 webhook；只能发到机器人所在群 |
| Yuanbao | 见 gateway 配置 | 走 bot 会话凭证，与 DingTalk 机制不同 |

其他平台（Telegram/Discord 等）：bot token 即出站凭证，没有"会话 webhook"这一层，主动投递通常开箱即用。

## Pitfalls

- **群机器人 webhook 不能私聊指定账号**：`oapi.dingtalk.com/robot/send` 只能发到机器人所在**群**。用户说"发给我的钉钉号 xxx"时，正确姿势是拉用户进机器人群，cron 投递到群（`DINGTALK_HOME_CHANNEL` 设为群 chat_id）。要 DM 特定用户需企业应用级消息 API（`agentId` + `corpconversation/asyncsend_v2`），复杂度高一个量级，非必要不做。
- **关键词安全模式**：钉钉要求消息内容含设定关键词（如 `Hermes`），否则返回 310000 关键词不匹配。Hermes payload 的 markdown title 固定为 "Hermes"，所以关键词设为 `Hermes` 最稳；自定义 cron prompt 时给消息加固定前缀即可。
- **别把「回复正常」当「投递正常」**：聊天 OK 不能证明 cron 投递 OK——两条路径配置完全独立。
- **`hermes send --to dingtalk` 失败**：同样走 `standalone_sender_fn`，报错即验证了缺 webhook 配置，也是验证配置是否生效的最快手段。

## 参考

- `references/dingtalk-webhook.md` — DingTalk 主动投递完整实证：源码位置、错误字符串、一次完整排查会话（2026-08 李渔文件 cron 投递失败案例）