# 钉钉 webhook 完整配置实例 (2026-08)

实际解决问题：cron 投递报 `delivery error: DingTalk not configured`。本文件记录完整诊断路径与验证结果。

## 错误原文（决定性证据）

```
ERROR cron.scheduler: Job '<job_id>': delivery error: DingTalk not configured.
Set DINGTALK_WEBHOOK_URL env var or webhook_url in dingtalk platform extra config.
```

同一问题还可能先出现（live adapter 阶段）：

```
live adapter delivery to dingtalk:<chat_id> failed: No valid session_webhook available.
Reply must follow an incoming message.; delivery error: DingTalk not configured. ...
WARNING hermes_plugins.dingtalk_platform.adapter: [Dingtalk] No valid session_webhook for chat_id=<chat_id>
```

## 关键代码位置（Hermes v0.20.0）

- `plugins/platforms/dingtalk/adapter.py` 行 ~1715：standalone_sender_fn 读取
  `webhook_url = extra.get("webhook_url") or os.getenv("DINGTALK_WEBHOOK_URL", "")`
- `plugins/platforms/dingtalk/adapter.py` 行 ~1706：注释确认此路径用于
  "cross-platform / cron delivery ... when cron runs separately from the gateway"
- `cron/scheduler.py` 行 ~3153：每次 job 运行前 `load_hermes_dotenv()` 重载 .env

## 本次会话实操记录

1. `.env` 原有：`DINGTALK_CLIENT_ID` / `DINGTALK_CLIENT_SECRET`（接收通道，Stream 模式）
2. 追加：`DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=<token>`（第 487 行）
3. 直发验证：curl POST 返回 `{"errcode":0,"errmsg":"ok"}`
4. 端到端验证：一次性 cron job（`schedule: 55 6 * * *`, `repeat: 1`, `deliver: dingtalk`）
   → 运行后 `last_status: ok`, `last_delivery_error: null`
5. gateway 未重启，webhook 已生效 —— **证明 cron 重载 .env 无需重启**

## 安全模式验证结论

钉钉自定义机器人三种安全设置：
- **自定义关键词**（本次选此，关键词 `Hermes`）：✔ 可行，消息需含关键词（Hermes markdown title 固定为 "Hermes"，天然满足）
- **加签（HMAC-SHA256）**：✘ Hermes 发送端无签名逻辑，必失败
- **IP 白名单**：✔ 需固定出口 IP，云服务器可用

## 遗留限制

- 群机器人 webhook 只能发所属群，无法主动私聊
- 若需 DM 主动投递：企业应用机器人（agentId + corpconversation 消息接口）
- 用户当前监控任务 `deliver: all`（钉钉+元宝）；元宝通道独立，不受此配置影响