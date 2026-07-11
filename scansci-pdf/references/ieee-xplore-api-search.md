# IEEE Xplore REST API 直接搜索

scansci-pdf search 底层依赖 OpenAlex，有 1-6 个月索引延迟。IEEE Xplore 的 REST API 可绕过此限制直接搜索。

## 端点

```
POST https://ieeexplore.ieee.org/rest/search
Content-Type: application/json
Referer: https://ieeexplore.ieee.org/
Origin: https://ieeexplore.ieee.org
```

## 请求体

```json
{
  "queryText": "rolling bearing fault diagnosis attention network",
  "pageNumber": 1,
  "rowsPerPage": 10,
  "returnFacets": ["ALL"],
  "highlight": true
}
```

## 响应结构

```json
{
  "records": [
    {
      "articleTitle": "Rolling Bearing Fault Diagnosis Based on ...",
      "doi": "10.1109/TIM.2024.xxxxxxx",
      "authors": [{"preferredName": "First Last", "lastName": "Last", ...}],
      "publicationYear": "2024",
      "publicationTitle": "IEEE Transactions on Instrumentation and Measurement",
      "abstract": "...",
      "articleNumber": "12345678"
    }
  ],
  "totalRecords": 15
}
```

- `totalRecords = 0` 且 `records = []` = 论文确定不在 IEEE 数据库中
- 无需认证 / 无需 Cookie
- 返回的是基于全文索引的匹配结果（不只是标题）

## 与 scansci-pdf search 的区别

| 维度 | scansci-pdf search | IEEE REST API |
|------|-------------------|---------------|
| 数据源 | OpenAlex | IEEE Xplore 直接索引 |
| 索引延迟 | 1-6 个月 | 上线即收录 |
| 精确度 | 摘要级匹配 | 全文级匹配 |
| 限流 | 无显著限流 | 无显著限流 |

## 典型用法

```bash
# 搜索特定标题
curl -s -X POST -H "Content-Type: application/json" \
  -H "Referer: https://ieeexplore.ieee.org/" \
  -d '{"queryText":"Vibration-ECAPA rolling bearing","pageNumber":1,"rowsPerPage":10}' \
  "https://ieeexplore.ieee.org/rest/search" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r.get('articleTitle'),'|',r.get('doi','')) for r in d.get('records',[])]"

# 按出版物过滤（可在 queryText 中加出版名称）
curl -s -X POST -H "Content-Type: application/json" \
  -H "Referer: https://ieeexplore.ieee.org/" \
  -d '{"queryText":"ECAPA bearing fault diagnosis","pageNumber":1,"rowsPerPage":10}' \
  "https://ieeexplore.ieee.org/rest/search"
```

## 注意

- 此 API 返回的是 JSON，不是 HTML。如果返回 HTML（如 405 页面），说明缺少 `Content-Type: application/json` header 或请求方式不是 POST
- GET 请求到同一 URL 会返回 405 Method Not Allowed
- 不要用这个 API 下载全文——它只提供元数据搜索