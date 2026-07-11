# OpenAlex 原始 API 搜索（绕过 scansci-pdf 封装）

scansci-pdf 的 `search` 命令对 OpenAlex 查询参数做了简化，遇到复杂查询或需要精确控制时，直接调用 OpenAlex API 更灵活。

## 基础搜索

```bash
curl -s "https://api.openalex.org/works?filter=title_and_abstract.search:KEYWORD&per_page=10"
```

## 常用过滤器

| 过滤器 | 示例 | 说明 |
|--------|------|------|
| `title_and_abstract.search` | `title_and_abstract.search:ECAPA` | 标题+摘要关键词 |
| `publication_year` | `publication_year:2024` | 精确年份 |
| `authorships.author.display_name.search` | `authorships.author.display_name.search:Chen` | 作者姓氏 |
| `primary_location.source.display_name` | `primary_location.source.display_name:IEEE` | 出版物名称 |
| `is_oa` | `is_oa:true` | 仅开放获取 |
| `type` | `type:article` | 论文类型（article/review/book-chapter） |
| `cited_by_count` | `cited_by_count:>10` | 引用数过滤 |

## 多条件组合

用逗号 `,` 连接多个条件（AND 语义）：

```bash
# 2024 年作者 Chen 且含 ECAPA
curl -s "https://api.openalex.org/works?filter=authorships.author.display_name.search:Chen,title_and_abstract.search:ECAPA,publication_year:2024"

# 2024 年 IEEE 期刊的 bearing fault diagnosis 论文
curl -s "https://api.openalex.org/works?filter=title_and_abstract.search:bearing,publication_year:2024,primary_location.source.display_name:IEEE&per_page=20"
```

## 排序

```bash
# 按相关性降序
...&sort=relevance_score:desc

# 按引用数降序
...&sort=cited_by_count:desc

# 按出版日期降序
...&sort=publication_date:desc
```

## 分页

```bash
# 每页 50 条，第 2 页
...&per_page=50&page=2
```

## 响应解析

```python
import json, urllib.request

url = "https://api.openalex.org/works?filter=title_and_abstract.search:ECAPA,publication_year:2024&per_page=50"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read())
    print(f"Total: {data['meta']['count']}")
    for w in data['results']:
        authors = [a['author']['display_name'] for a in w.get('authorships', [])]
        print(f"{w['title']} | {w.get('doi','')} | {', '.join(authors[:3])}")
```

## 已知限制

- OpenAlex 对 2024 年下半年发表的论文有 1-6 个月索引延迟
- 如果 `meta.count = 0`，不代表论文不存在——只代表 OpenAlex 还没收录
- 此时应降级到 IEEE Xplore REST API 直接搜索（见 `references/ieee-xplore-api-search.md`）

## 对比：scansci-pdf search vs 直接 OpenAlex

| 维度 | scansci-pdf search | 直接 OpenAlex API |
|------|-------------------|-------------------|
| 参数灵活性 | 有限（仅 query, year_from, limit, sort） | 全部 OpenAlex 参数 |
| 多条件组合 | 不支持 | 支持逗号分隔 AND 组合 |
| 作者过滤 | 不支持 | 支持 `authorships.author.display_name.search` |
| 输出 | 精简字段 | 全部字段（含 citations_by_year, referenced_works 等） |