---
name: hermes-gateway-delivery
description: "Fix Hermes cron delivery 'not configured' webhook errors."
---

# Hermes Gateway Delivery (平台主动投递配置)

诊断与修复 Hermes 消息平台（DingTalk 钉钉、Feishu 飞书、WeCom 企微等）的**主动出站投递**：cron 定时任务、`hermes send`、跨平台通知。

## 核心机制：双通道模型

几乎所有 Hermes 平台插件都有两条发消息路径：

| 路径 | 触发场景 | 依赖 |
|:-----|:---------|:-----|
| **回复路径** | 用户发消息 → agent 回复 | 入站消息自带的 `session_webhook`（临时、随消息下发、有过期时间） |
| **主动投递路径** | cron 投递、`hermes send`、定时通知（与入站消息无关） | **静态 webhook**：`<PLATFORM>_WEBHOOK_URL` 环境变量 或 platform extra 里的 `webhook_url` |

**诊断信号** —— 出错信息直接指向缺配置：

```
cron.scheduler: delivery error: DingTalk not configured.
Set DINGTALK_WEBHOOK_URL env var or webhook_url in dingtalk platform extra config.
```

- `No valid session_webhook for chat_id=...` → 尝试主动投递但只有 session webhook 缓存（通常是 gateway 重启后或 cron 与 gateway 分离运行）
- `delivery error: <Platform> not configured. Set <PLATFORM>_WEBHOOK_URL ...` → 静态 webhook 未配置，走 `standalone_sender_fn`（见 `plugins/platforms/<platform>/adapter.py`，模式：`extra.get("webhook_url") or os.getenv("<PLATFORM>_WEBHOOK_URL")`）

## 解决步骤（以钉钉为例，其他平台类推）

1. **在平台侧创建机器人 webhook**：
   - 钉钉：群设置 → 机器人 → 自定义（Webhook 接入）
   - ⚠️ 安全设置选 **自定义关键词**（如 `Hermes`），**不要选"加签"**——Hermes 发送端未实现 HMAC 签名，加签必失败（钉钉返回 310000）
   - 若选关键词模式，消息内容必须含该关键词，否则报"关键词不匹配"
2. **写入配置（二选一）**：
   ```bash
   echo 'DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx' >> ~/.hermes/.env
   # 或
   hermes config set gateway.platforms.dingtalk.webhook_url "https://oapi.dingtalk.com/robot/send?access_token=xxx"
   ```
3. **验证连通性**（curl 直发，`errcode:0` = 通）：
   ```bash
   curl -s -X POST "$DINGTALK_WEBHOOK_URL" -H "Content-Type: application/json" \
     -d '{"msgtype":"text","text":{"content":"Hermes 测试消息"}}'
   ```
4. **端到端验证**：建一次性 cron 任务 `deliver=<platform>`（schedule 用 cron 表达式，如 `55 6 * * *`，duration 最短 30m），跑完后查 `cronjob list` 的 `last_status=ok` 且 `last_delivery_error=null`。

## 关键结论：改 .env 后【不需要】重启 gateway

`cron/scheduler.py` 每次任务运行前都会重新加载 `.env` 和 config（`load_hermes_dotenv`，代码注释明确写 "changes take effect without a gateway restart"）。因此：

- 修改 `~/.hermes/.env` 中的 webhook/密钥 → **下一个 cron tick 自动生效**
- 不要为此冒险重启 gateway（见下面 Pitfall）

## Pitfalls

### ❌ 无法从 gateway 进程内部重启 gateway
Hermes 工具安全层拦截任何含 `restart`/`systemctl ... hermes-gateway` 的命令（防 SIGTERM 传播自杀），**包括通过 `/tmp/*.sh` 脚本间接执行同样被拦**。对策：
- 优先选择不需要重启的配置变更（.env → cron 自动重载）
- 必须重启时，让用户在 gateway 之外的独立 shell 执行 `hermes gateway restart`，或直接 `systemctl --user restart hermes-gateway`

### ❌ 群机器人 webhook 只能发到"它所在的群"，不能私聊
"把消息发到用户钉钉号 xxx 的独立 webhook" 不存在——自定义机器人归属群，用户必须在该群里才能收到。若要主动推送进 DM：
- 企业应用级机器人 API（需 `agentId` + 消息接口），复杂度高一档，一般不建议
- 或把该用户拉进机器人所在群，投递目标指向群

### ❌ 安全模式选择错误
钉钉自定义机器人强制要求三种安全设置之一：自定义关键词 / 加签 / IP 白名单。Hermes 发送端只 POST 无签名 → **选"加签"必失败**。选"自定义关键词"需要消息含词；选"IP 白名单"需要固定出口 IP。

## 检查清单（快速定位）

```bash
# 1. 平台连上了吗（gateway_state.json）
cat ~/.hermes/gateway_state.json | grep -A2 platforms
# 2. webhook 配了吗
grep -n "<PLATFORM>_WEBHOOK_URL" ~/.hermes/.env
# 3. 最近投递错误（决定性证据）
grep -i "delivery error\|No valid session_webhook" ~/.hermes/logs/gateway.log | tail
# 4. 出错的 cron job 明细
hermes cron list   # 看 last_delivery_error 字段
```

## 参考

- 钉钉完整配置实例与错误原文：`references/dingtalk-webhook.md`