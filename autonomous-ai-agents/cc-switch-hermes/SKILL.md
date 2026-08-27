---
name: cc-switch-hermes
description: "cc-switch + Hermes providers: query, switch, DB, fallback."
---

# cc-switch + Hermes 集成

## 适用场景

- 用户问"当前配置了多少个模型"或"有哪些 provider 可用"
- 用户想切换 Hermes 的 provider 或模型
- 用户想配置 Hermes 的自动 fallback 链
- 需要探查 cc-switch 数据库中存储的 provider 配置

## 背景

`cc-switch` 是一个统管 Claude Code、Codex、Gemini、OpenCode、Hermes 等 AI CLI 工具的 provider/MCP/skill/prompt 配置管理器。二进制安装于 `~/.local/bin/cc-switch`，数据存储于 SQLite 数据库。

## 核心命令

### 列出 Hermes 的 provider

```bash
cc-switch -a hermes provider list
```

输出格式：ID、Name、API URL。当前选中的 provider 带 ✓ 标记。

### 切换 provider

```bash
cc-switch -a hermes use <provider-id>
# 例如：cc-switch -a hermes use deepseek4
```

切换时会自动更新 Hermes 的 `~/.hermes/config.yaml`（model.default, base_url, api_key 等字段）。

### 获取详细列表

```bash
cc-switch -a hermes provider list -v    # 带 DEBUG 日志，显示导入过程
```

## 数据库探查

cc-switch 的 provider 配置存储在 SQLite 数据库 `~/.cc-switch/cc-switch.db` 的 `providers` 表中。

关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT | provider 唯一标识（如 `sensenova-deepseek-v4-flash`） |
| `app_type` | TEXT | 应用类型：`hermes`、`claude`、`codex` 等 |
| `name` | TEXT | 显示名称 |
| `settings_config` | TEXT | **JSON 字符串**，包含完整配置 |
| `is_current` | INTEGER | 是否为当前选中（0/1） |
| `in_failover_queue` | INTEGER | 是否在 failover 队列中 |
| `category` | TEXT | provider 分类（`cn_official`、`aggregator` 等） |
| `icon` | TEXT | 图标标识 |
| `meta` | TEXT | JSON 元数据（用量脚本、端点配置等） |

### 查询所有 Hermes provider

```python
import sqlite3, json
db = sqlite3.connect('/root/.cc-switch/cc-switch.db')
rows = db.execute(
    "SELECT id, name, settings_config FROM providers WHERE app_type='hermes'"
).fetchall()
for row in rows:
    cfg = json.loads(row[2])
    print(f"{row[0]} → {cfg.get('base_url')} model={cfg.get('model')}")
```

### `settings_config` JSON 结构

```json
{
  "name": "provider-name",
  "base_url": "https://api.example.com/v1",
  "api_key": "sk-...",
  "model": "model-name",
  "api_mode": "chat_completions",
  "models": [
    {"name": "display-name", "id": "model-id"},
    ...
  ],
  "rate_limit_delay": 0.2,
  "_cc_source": "custom_providers"
}
```

### `provider_endpoints` 表

辅助表，记录 provider 的端点 URL：

```sql
SELECT * FROM provider_endpoints WHERE app_type='hermes';
```

## Hermes 原生 fallback 配置

### ⚠️ cc-switch failover 不支持 Hermes

`cc-switch failover` 子命令对 `-a hermes` 无效，报错：
```
Error: 无效输入: failover is not supported for hermes
```

该功能仅适用于 Claude Code、Codex 等应用。

### 正确的方案：Hermes `fallback_providers`

在 `~/.hermes/config.yaml` 中配置：

```yaml
fallback_providers:
  - provider: custom
    model: glm-5.2
    base_url: https://token.sensenova.cn/v1
    api_key: "${SN_API_KEY}"
  - provider: custom
    model: deepseek-ai/deepseek-v4-flash-0731
    base_url: https://integrate.api.nvidia.com/v1
    api_key: "${NVIDIA_API_KEY}"
```

关键点：
- 每个条目支持 `provider`、`model`、`base_url`、`api_key` 四个字段
- `api_key` 支持 `${VAR}` 环境变量引用（从 `.env` 读取）
- 改配置**实时生效**，无需重启 gateway（代码 `_refresh_fallback_model` 机制）
- 主模型请求失败后按序依次尝试 fallback 链
- 当前 `fallback_providers: []` 为空时主模型一挂直接断联

### 读取当前 fallback 链

```python
import yaml
cfg = yaml.safe_load(open('/root/.hermes/config.yaml'))
print(cfg.get('fallback_providers', []))
```

## credential_pool（auth.json）

Hermes 的 provider 凭据池存储在 `~/.hermes/auth.json` 的 `credential_pool` 字段：

```python
import json
d = json.load(open('/root/.hermes/auth.json'))
pool = d.get('credential_pool', {})
for k, v in pool.items():
    print(f"{k}: {len(v)} 条凭据")
```

## 其他相关表

| 表名 | 用途 |
|------|------|
| `provider_health` | 健康检查记录（`is_healthy`、`consecutive_failures`、`last_error`） |
| `stream_check_logs` | 流式端点可达性检查日志 |
| `proxy_config` | 本地代理配置（`app_type` 区分 claude/codex/hermes） |
| `proxy_failover_live_snapshots` | 代理 failover 实时快照 |
| `settings` | 全局设置（key-value） |

## Pitfalls

### ❌ cc-switch 的 api_key 与 .env 不匹配

cc-switch 将每个 provider 的 api_key 独立存储在 `settings_config` JSON 中，而 `~/.hermes/.env` 中的环境变量（如 `SN_API_KEY`、`NVIDIA_API_KEY`）可能对应不同的 key 值。使用 `${VAR}` 引用时需确认对应关系——cc-switch 切换时直接写 config.yaml 的明文 key，不经过环境变量。

### ❌ 修改 config.yaml 被安全策略拦截

Hermes 的安全策略（Tirith）会拦截对 `~/.hermes/config.yaml` 的直接写入（`patch`、`write_file` 工具）。解决方案：
1. 使用 `hermes config set <key> <value>` 设置简单字段
2. 对于复杂结构（如 `fallback_providers` 数组），使用 `python3 -c` 通过终端写入（需用户交互批准）