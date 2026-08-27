# DingTalk 主动投递 — 完整实证（2026-08 排查记录）

## 现场：用户报错

用户转述报错：「钉钉账号 c13302108289 的独立 webhook 未配置」。

背景：上一条会话（2026-08-13）用户要求把 `/root/《李渔全集》研究价值与学术前沿.md` 发送到钉钉号 `c13302108289`，agent 创建了一次性 cron job（id `51d1b9384a29`）投递，投递失败。次日用户看到错误来问。

## 根因（找到的确凿证据链）

1. 天天聊天都正常 → 回复路径 OK（每条入站消息带 session_webhook）。
2. cron 调度日志明确报错：

```
/root/.hermes/logs/agent.log:
ERROR [20260813_204748_6ab9a546] cron.scheduler: Job '51d1b9384a29':
delivery error: DingTalk not configured. Set DINGTALK_WEBHOOK_URL env var
or webhook_url in dingtalk platform extra config.
```

3. 早前还有一条独立警告，是**回复路径**的正常行为：

```
2026-08-07 09:02:50 WARNING hermes_plugins.dingtalk_platform.adapter:
[Dingtalk] No valid session_webhook for chat_id=cidq53JOMF4vgFtj9bqUSWKHjgiU9VOsGKU7rEIGl8dCFA=
```

（8-07 09:02 恰好是每周五国网冀北监控 cron job `01ca198da00a` 的运行时刻——cron 投递时没有入站消息，session_webhook 缓存为空。注意该 cron 输出的 FAILED 是 content_policy_blocked，与投递错误是两码事，别混淆。）

## 源码定位

插件根目录：`/usr/local/lib/hermes-agent/plugins/platforms/dingtalk/`

- `plugin.yaml` `optional_env:` 列出 `DINGTALK_WEBHOOK_URL` — "Static robot webhook URL for cross-platform / cron delivery"
- `adapter.py` `standalone_sender_fn`（约 1700-1740 行）— 出站投递实现：

```python
webhook_url = extra.get("webhook_url") or os.getenv("DINGTALK_WEBHOOK_URL", "")
if not webhook_url:
    return {"error": "DingTalk not configured. Set DINGTALK_WEBHOOK_URL env var or webhook_url in dingtalk platform extra config."}
# POST https://oapi.dingtalk.com/robot/send  {msgtype:text}
```

- `adapter.py` `_get_valid_webhook` / `_session_webhooks` dict（约 1165-1180 行）— 回复路径的 chat_id → (webhook, expired_ms) 缓存
- 官方文档：`website/docs/user-guide/messaging/dingtalk.md` 有 "No session_webhook available" 一节（约 260 行），确认这是钉钉正常限制：只能回复近期收到过的消息。

## 排查先后顺序（本次实战顺序）

1. `hermes config path` / `hermes config` → 找 dingtalk 段落（无 gateway.platforms 段，只有 `DINGTALK_HOME_CHANNEL` 顶层项）
2. `grep -i ding ~/.hermes/logs/gateway.log | tail` → 拿到两个关键警告（上面的 #2 #3）
3. `grep -rn "独立 webhook"` 全库 → 无此文案（中文是转述，源错误是英文）
4. `grep -n "session_webhook\|webhook" adapter.py` → 双路径机制浮出
5. `sed -n '960,1080p' adapter.py` → send() 实现：先 metadata.session_webhook → 再查缓存 → 都没有则报错
6. 检查 cron 输出目录 `~/.hermes/cron/output/`：目录名 = job_id，文件名 = 时间戳，与日志时间戳精确对齐
7. `grep -i "51d1b9384a29" ~/.hermes/logs/*.log` → 拿到 delivery error 全文

## 修复验证

```bash
hermes send --to dingtalk "Hermes 测试消息"   # 成功后输出 SendResult success
hermes gateway restart                        # 改完配置必须重启
```

## 关键事实备忘

- 钉钉 Stream Mode 连接用 `DINGTALK_CLIENT_ID`/`DINGTALK_CLIENT_SECRET`（接收方向，`.env` 里已有）
- 本机 channel_directory.json 显示两个钉钉 DM：陈冀川（cidq53…=，即 DINGTALK_HOME_CHANNEL）、陆彬（cidodxpiKu…=）
- 群机器人 webhook 的 URL 格式：`https://oapi.dingtalk.com/robot/send?access_token=<token>`，仅机器人所在群可收