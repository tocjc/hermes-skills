---
name: firecrawl
description: "Firecrawl 网页抓取与搜索 API — 将任意 URL 转为 LLM-ready Markdown/JSON。"
---

# Firecrawl — 网页数据采集 API

[Firecrawl](https://github.com/firecrawl/firecrawl) 是开源网页数据采集 API，将任意 URL 转为 **LLM-ready 的 Markdown 或结构化 JSON**。支持搜索+爬取、全站爬虫、页面交互、Agent 自主采集。

- **仓库**: https://github.com/firecrawl/firecrawl (167k+ ⭐, AGPL-3.0)
- **官网**: https://firecrawl.dev
- **文档**: https://docs.firecrawl.dev
- **API 参考**: https://docs.firecrawl.dev/api-reference/introduction

## 前置条件

| 方式 | 条件 |
|------|------|
| **Cloud API（推荐）** | 在 https://firecrawl.dev 注册获取 API Key（格式: `fc-xxx`） |
| **CLI 工具** | `npx -y firecrawl-cli@latest init --all --browser` |
| **MCP 集成** | 配置 `mcpServers` 中的 `firecrawl-mcp` |
| **自托管** | Docker Compose 部署，详见 [Self-Host Guide](https://docs.firecrawl.dev/contributing/self-host) |

## 核心 API 端点（v2）

所有 API 调用均需 Bearer Token 认证：

```
Authorization: Bearer fc-YOUR_API_KEY
```

### 1. Search — 搜索并获取页面内容

```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/search' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "your search query",
    "limit": 5
  }'
```

响应示例:
```json
{
  "success": true,
  "data": [
    {
      "url": "https://example.com",
      "title": "Page Title",
      "markdown": "# Markdown Content...",
      "metadata": { "sourceURL": "..." }
    }
  ]
}
```

### 2. Scrape — 爬取单页

```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/scrape' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"]
  }'
```

可选 formats: `markdown`, `html`, `rawHtml`, `screenshot`, `json`（通过 extract 选项）

### 3. Interact — 页面交互（点击/输入/滚动）

先爬取获取 `scrapeId`，然后交互：

```bash
curl -X POST 'https://api.firecrawl.dev/v2/scrape/SCRAPE_ID/interact' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Search for '\''mechanical keyboard'\''"}'
```

### 4. Agent — 自主数据采集（无需指定 URL）

描述需求，AI 自动搜索、导航、采集：

```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/agent' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Find the pricing plans for Notion"
  }'
```

Agent 支持结构化输出（JSON Schema）：

```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/agent' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Find the founders of Firecrawl",
    "schema": {
      "type": "object",
      "properties": {
        "founders": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "role": {"type": "string"}
            }
          }
        }
      }
    }
  }'
```

### 5. Crawl — 全站爬取

```bash
# 发起爬取任务
curl -s -X POST 'https://api.firecrawl.dev/v2/crawl' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://docs.firecrawl.dev",
    "limit": 50,
    "scrapeOptions": {
      "formats": ["markdown"]
    }
  }'

# 返回 job ID，轮询状态
curl -s -X GET 'https://api.firecrawl.dev/v2/crawl/JOB_ID' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY'
```

### 6. Map — 站点 URL 发现

```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/map' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

支持 `search` 参数筛选特定路径:
```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/map' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "search": "pricing"}'
```

### 7. Batch Scrape — 批量爬取

```bash
curl -s -X POST 'https://api.firecrawl.dev/v2/batch/scrape' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": ["https://example.com/page1", "https://example.com/page2"],
    "formats": ["markdown"]
  }'
```

## Python SDK 用法

```bash
pip install firecrawl-py
```

```python
from firecrawl import Firecrawl

app = Firecrawl(api_key="fc-YOUR_API_KEY")

# 爬取单页
doc = app.scrape("https://example.com", formats=["markdown"])
print(doc.markdown)

# 搜索
results = app.search("search query", limit=5)
for r in results.data:
    print(r.title, r.url)

# Agent 自主采集
result = app.agent(prompt="Find the founders of Stripe")
print(result.data)

# 全站爬取（自动轮询）
docs = app.crawl("https://docs.example.com", limit=50)
for doc in docs.data:
    print(doc.metadata.source_url)

# 站点地图
links = app.map("https://example.com", search="pricing")
```

## 作为 Hermes Agent 的外部工具使用

### 方式 A: 直接 curl 调用

在 Hermes 的 terminal 中直接调用 Firecrawl API 获取网页数据：

```bash
# 搜索
curl -s -X POST 'https://api.firecrawl.dev/v2/search' \
  -H 'Authorization: Bearer fc-YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"query": "some topic", "limit": 5}' | python3 -m json.tool
```

### 方式 B: 通过 MCP 集成

在 `~/.hermes/config.yaml` 中配置：

```yaml
mcpServers:
  firecrawl:
    command: npx
    args:
      - -y
      - firecrawl-mcp
    env:
      FIRECRAWL_API_KEY: fc-YOUR_API_KEY
```

### 方式 C: CLI 工具

```bash
npx -y firecrawl-cli@latest init --all --browser
firecrawl search "query" --limit 5
firecrawl scrape https://example.com
```

## 典型场景速查表

| 场景 | 推荐 API | 说明 |
|------|----------|------|
| 搜索网页+获取内容 | Search | 类似 Google + 自动爬取结果 |
| 爬取单个页面内容 | Scrape | 支持 JS 渲染、动态内容 |
| 全站内容采集 | Crawl | 自动遍历所有页面 |
| 发现站点结构 | Map | 获取所有 URL 清单 |
| 需要结构化数据 | Agent + schema | 自动定位并提取 |
| 模拟用户操作 | Interact | 点击、搜索、翻页 |
| 批量采集 | Batch Scrape | 并发爬取多个 URL |

## 关键特性

- **96% 网页覆盖率**（含 JS 重页面）
- **P95 延迟 3.4s**（百万级页面基准）
- **LLM-ready 输出**：Markdown 比原始 HTML 节省 90% tokens
- **自动处理**：代理轮换、速率限制、反爬虫绕过
- **支持媒体解析**：PDF、DOCX 等文档
- **尊重 robots.txt**（默认开启）
- **Agent 模型选择**：`spark-1-mini`（便宜 60%）/ `spark-1-pro`（复杂任务）

## 已知限制

- **API Key 需要注册**：cloud.firecrawl.dev 注册获取
- **免费额度有限**：查看 [Pricing](https://firecrawl.dev/pricing) 了解免费额度
- **自托管需要基础设施**：Docker Compose + Redis + PostgreSQL + RabbitMQ
- **Crawl 任务异步**：需要轮询 job 状态（SDK 自动处理）
- **Agent 功能**（v2/agent）仅在 cloud 版本可用
- **Hermes 内置 web 工具**：`web_search` / `web_extract` 直接使用 Firecrawl 基础设施，需要配置 `FIRECRAWL_API_KEY` 环境变量