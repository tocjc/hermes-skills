# Firecrawl API v2 Endpoints Quick Reference

Base URL: `https://api.firecrawl.dev/v2`

## Authentication
All requests: `Authorization: Bearer fc-YOUR_API_KEY`

## Endpoints

| Endpoint | Method | Async? | Description |
|----------|--------|--------|-------------|
| `/v2/search` | POST | No | Search web + scrape results |
| `/v2/scrape` | POST | No | Scrape single URL |
| `/v2/scrape/{id}/interact` | POST | No | Interact with scraped page |
| `/v2/agent` | POST | Yes | Autonomous data gathering |
| `/v2/agent/{id}` | GET | — | Check agent job status |
| `/v2/crawl` | POST | Yes | Crawl entire website |
| `/v2/crawl/{id}` | GET | — | Check crawl job status |
| `/v2/map` | POST | No | Discover site URLs |
| `/v2/batch/scrape` | POST | Yes | Scrape multiple URLs |

## Common ScrapeOptions

```json
{
  "formats": ["markdown", "html", "rawHtml", "screenshot"],
  "onlyMainContent": true,
  "includeTags": ["article", "main"],
  "excludeTags": ["nav", "footer", "header"],
  "waitFor": 2000,
  "timeout": 30000
}
```

## CrawlOptions

```json
{
  "limit": 100,
  "maxDepth": 3,
  "scrapeOptions": { "formats": ["markdown"] },
  "allowExternalLinks": false,
  "ignoreSitemap": false
}
```

## AgentOptions

```json
{
  "prompt": "Describe what data to collect",
  "schema": { "type": "object", "properties": {...} },
  "urls": ["https://..."],
  "model": "spark-1-mini",
  "maxSources": 10
}
```

## Response Status Values

Crawl/Agent async jobs:
- `scraping` — in progress
- `completed` — done
- `failed` — error
- `cancelled` — user cancelled