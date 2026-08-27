# cc-switch SQLite 数据库参考

## 数据库位置

- 主数据库：`~/.cc-switch/cc-switch.db`
- 其他副本：`~/.hermes/scripts/cc-switch.db`（可能是旧版/备份）

## 表结构

### providers

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 唯一标识 |
| app_type | TEXT | 应用类型（hermes / claude / codex / gemini / opencode） |
| name | TEXT | 显示名称 |
| settings_config | TEXT | JSON：{name, base_url, api_key, model, models[], api_mode, rate_limit_delay, _cc_source} |
| website_url | TEXT | 服务商网站 |
| category | TEXT | official / aggregator / cn_official / null |
| created_at | INTEGER | 时间戳 |
| sort_index | INTEGER | 排序 |
| notes | TEXT | 备注 |
| icon | TEXT | 图标标识 |
| icon_color | TEXT | 颜色 |
| meta | TEXT | JSON：{usage_script, endpointAutoSelect, liveConfigManaged} |
| is_current | INTEGER | 0/1 |
| in_failover_queue | INTEGER | 0/1 |
| cost_multiplier | TEXT | "1.0" |
| limit_daily_usd | TEXT | null |
| limit_monthly_usd | TEXT | null |
| provider_type | TEXT | null |

### provider_endpoints

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | PK |
| provider_id | TEXT | 对应 providers.id |
| app_type | TEXT | 应用类型 |
| url | TEXT | 端点 URL |
| added_at | INTEGER | 时间戳 |

### provider_health

| 字段 | 类型 | 说明 |
|------|------|------|
| provider_id | TEXT | PK |
| app_type | TEXT | 应用类型 |
| is_healthy | INTEGER | 0/1 |
| consecutive_failures | INTEGER | 连续失败次数 |
| last_success_at | INTEGER | 时间戳 |
| last_failure_at | INTEGER | 时间戳 |
| last_error | TEXT | 最后错误信息 |
| updated_at | INTEGER | 更新时间戳 |

### stream_check_logs

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | PK |
| provider_id | TEXT | |
| provider_name | TEXT | |
| app_type | TEXT | |
| status | TEXT | operational / error |
| success | INTEGER | 0/1 |
| message | TEXT | 结果描述 |
| response_time_ms | INTEGER | 响应时间（毫秒） |
| http_status | INTEGER | HTTP 状态码 |
| model_used | TEXT | 测试用的模型 |
| retry_count | INTEGER | 重试次数 |
| tested_at | INTEGER | 时间戳 |

### proxy_config

| 字段 | 类型 | 说明 |
|------|------|------|
| app_type | TEXT | PK |
| proxy_enabled | INTEGER | 0/1 |
| listen_address | TEXT | 127.0.0.1 |
| listen_port | INTEGER | 15721（claude）/ 15724（hermes 偏好） |
| enable_logging | INTEGER | 0/1 |
| enabled | INTEGER | 0/1 |
| auto_failover_enabled | INTEGER | 0/1 |
| max_retries | INTEGER | |
| streaming_first_byte_timeout | INTEGER | 秒 |
| streaming_idle_timeout | INTEGER | 秒 |
| non_streaming_timeout | INTEGER | 秒 |
| circuit_failure_threshold | INTEGER | 熔断阈值 |
| circuit_success_threshold | INTEGER | 熔断恢复阈值 |
| circuit_timeout_seconds | INTEGER | 熔断超时 |
| circuit_error_rate_threshold | REAL | 错误率阈值 |
| circuit_min_requests | INTEGER | 最小请求数 |
| default_cost_multiplier | TEXT | 成本乘数 |
| pricing_model_source | TEXT | response / config |
| live_takeover_active | INTEGER | 0/1 |
| created_at | TEXT | ISO 时间 |
| updated_at | TEXT | ISO 时间 |

### model_pricing

| 字段 | 类型 | 说明 |
|------|------|------|
| model_id | TEXT | 模型 ID |
| display_name | TEXT | 显示名称 |
| input_cost_per_million | TEXT | 每百万输入 tokens 价格 |
| output_cost_per_million | TEXT | 每百万输出 tokens 价格 |
| cache_read_cost_per_million | TEXT | 缓存读取价格 |
| cache_creation_cost_per_million | TEXT | 缓存创建价格 |

### settings

| 字段 | 类型 | 说明 |
|------|------|------|
| key | TEXT | PK |
| value | TEXT | JSON 值或字符串 |

## 常用查询

### 查询所有 Hermes provider 的完整配置

```python
import sqlite3, json
db = sqlite3.connect('/root/.cc-switch/cc-switch.db')
rows = db.execute(
    "SELECT id, name, settings_config FROM providers WHERE app_type='hermes'"
).fetchall()
for row in rows:
    cfg = json.loads(row[2])
    print(f"--- {row[0]} ({row[1]}) ---")
    print(f"  base_url: {cfg.get('base_url')}")
    print(f"  model: {cfg.get('model')}")
    print(f"  api_mode: {cfg.get('api_mode', 'N/A')}")
    models = cfg.get('models', [])
    if models:
        print(f"  models ({len(models)}):")
        for m in models:
            print(f"    - {m.get('id')} ({m.get('name', 'N/A')})")
    print()
```

### 查询 Provider 健康状态

```python
rows = db.execute(
    "SELECT provider_id, is_healthy, consecutive_failures, last_error "
    "FROM provider_health WHERE app_type='hermes'"
).fetchall()
for r in rows:
    print(f"{r[0]}: healthy={r[1]} failures={r[2]} error={r[3]}")
```

### 查看代理配置

```python
rows = db.execute(
    "SELECT app_type, proxy_enabled, auto_failover_enabled, listen_port "
    "FROM proxy_config"
).fetchall()
for r in rows:
    print(f"{r[0]}: proxy={r[1]} failover={r[2]} port={r[3]}")
```