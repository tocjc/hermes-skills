---
name: scansci-pdf
description: >
  MCP-based academic paper downloader. Given a DOI, arXiv ID, paper title,
  or a list/`.bib` file, it downloads the full-text PDF by trying OA sources,
  Sci-Hub, publisher APIs, and institutional login in priority order.
  TRIGGER: "download this paper", DOI link, arXiv ID, "帮我下载论文",
  "搜索文献", "批量下载", "文献检索", paper list, .bib import, citation export.
  SKIP: conceptual discussion of papers (no MCP needed), non-academic PDFs.
---

# scansci-pdf — 学术论文下载 MCP 套件

## 架构概览

scansci-pdf 已注册为 Hermes MCP 服务器，所有工具以 `scansci_pdf_` 前缀暴露。
37 个工具覆盖：下载、搜索、批量、引文、机构登录、WebVPN、CARSI、Tor、诊断、配置。

## 核心工作流

### 快速下载单篇（零配置首选）

```
scansci_pdf_smart_download(identifier="10.1038/nature12373")
```

自动探测最优来源路径，无需手动指定任何参数。

也可直接用 CLI（零 token 开销）：
```bash
scansci-pdf get 10.1038/nature12373
scansci-pdf get 10.1038/nature12373 --no-bibtex
```

### 搜索 → 确认 → 下载

用户只给了论文标题或关键词时：

1. `scansci_pdf_search(query="YOUR_KEYWORDS", year_from=2020, limit=15, sort="cited_by_count")`
2. **让用户从结果中选择** → 记录选中的 DOI
3. `scansci_pdf_download(identifier="SELECTED_DOI")` 或批量下载

**关键原则：搜索后必须展示结果给用户确认，不要自动下载全部。**

### 批量下载

DOI 列表文件（每行一个 DOI 或 DOI URL）：
```
scansci_pdf_batch_download(identifiers=["10.1038/nature12373", "10.1126/science.aec6396"], output_dir="downloads")
```

`.bib` 文件导入：
```
scansci_pdf_import_bib(bib_file="/path/to/refs.bib")
```

参考文献列表文件（APA 格式 / DOI 列表 / .md 文件）：
1. `scansci_pdf_parse_list(file_path="/path/to/references.md")` — 查看解析结果
2. `scansci_pdf_resolve_and_download(file_path="/path/to/references.md")` — 自动补全缺失 DOI 后批量下载

### 从 Markdown 综述报告批量下载

当用户提供一份 Markdown 综述报告（含多个论文链接），需要从其中提取所有链接并批量下载时：

**推荐工作流（并行分治）：**

1. **提取链接**：用正则 `re.findall(r'\[论文链接\]\(([^)]+)\)', content)` 从 Markdown 中提取 URL 列表
2. **按出版商分类**：将 URL 分组（如 振动与冲击/jvs.sjtu.edu.cn、IEEE、MDPI、Nature、CSTAM 等）
3. **并行下载**：用 `delegate_task` 为每组创建一个子 Agent，各自下载后保存到统一目录

**关键技巧：**
- 对中文期刊摘要页，从 `<meta name="citation_pdf_url" content="...">` 提取真实 PDF 链接
- 对 MDPI 论文，DOI 模式为 `10.3390/s{volume}{issue}{article}`，但 MDPI 使用 Akamai CDN 可能封锁中国服务器 IP，备用方案：通过 OpenAlex 的 `open_access.oa_url` 字段获取带版本号的 PDF 链接
- 对 IEEE 付费论文，优先搜索作者个人网站（如 `zhao62.github.io`）
- 每个子 Agent 下载完报告文件大小和有效性（`file` 命令验证 `%PDF-` 开头）

**并行下载模板：**
```python
# 提取链接并分类后，为每个类别创建子任务
tasks = [
    {"goal": "下载 a 类论文...", "context": "..."},
    {"goal": "下载 b 类论文...", "context": "..."},
]
delegate_task(tasks=tasks)
```

### 下载完成后处理：PDF 批量重命名

来自综述报告的论文下载完成后，用户可能要求将 `caseN_xxx.pdf` 文件名改为实际论文标题。流程：

1. **建立编号→标题映射**：从报告 Markdown 中提取
   ```python
   import re
   content = open("综述报告.md").read()
   title_map = {}
   cases = content.split("### 案例 ")
   for case_block in cases[1:]:
       case_num = int(re.search(r'^(\d+)', case_block).group(1))
       title_match = re.search(r'\|\s*\*\*论文标题\*\*\s*\|\s*(.+?)\s*\|', case_block)
       if title_match:
           title_map[case_num] = title_match.group(1).strip()
   ```

2. **执行重命名**：用 `os.rename(old_path, new_path)` 逐个改名

3. **验证**：`file` 命令确认重命名后文件仍为有效 PDF

### 获取引文

```
scansci_pdf_citation(identifier="10.1038/nature12373", format="bibtex")
scansci_pdf_citation(identifier="10.1038/nature12373", format="ris")
scansci_pdf_citation(identifier="10.1038/nature12373", format="endnote")
```

### 推送到 Zotero

```
# 先下载，再推送（需要 Zotero API Key 已配置）
scansci_pdf_zotero_push(identifier="10.1038/nature12373", library_id="1234567", api_key="...")
```

## 付费墙 / 机构登录流程

当下载返回 `error_type="paywall"` 或 `action="login_required"` 时：

1. 调用 `scansci_pdf_login(identifier="同一DOI")` — 打开浏览器到论文页面
2. 提示用户："点击 Access through your institution → 选择你的机构 → 完成 SSO 登录 → 关闭浏览器"
3. 用户关闭浏览器后 cookies 自动保存到 `~/.scansci-pdf/cookies/`
4. 重试 `scansci_pdf_download(identifier="同一DOI")`
5. **一次登录，同出版商所有论文自动复用**（批量下载中只需登录一次）

## WebVPN / CARSI / EZProxy 配置

| 方式 | 配置命令 |
|------|---------|
| **WebVPN** | `scansci_pdf_instsci_schools(query="北京")` → `scansci_pdf_instsci_set_school(school="北京大学")` → `scansci_pdf_instsci_login()` |
| **CARSI** | `scansci_pdf_config_set(key="carsi_enabled", value="true")` + 设置 `carsi_idp_name` → `scansci_pdf_carsi_login(publisher="sciencedirect")` |
| **EZProxy** | `scansci_pdf_config_set(key="ezproxy_enabled", value="true")` + 设置 `ezproxy_login_url` → `scansci_pdf_ezproxy_login()` |

**大多数情况下 `scansci_pdf_login(identifier="DOI")` 就够了**，不需要手动配置上述方式。

## Elsevier API Key（推荐配置）

Elsevier/ScienceDirect 论文下载加速：

1. 去 https://dev.elsevier.com/ 注册获取 API Key
2. `scansci_pdf_elsevier_setup(api_key="YOUR_KEY")`
3. 可选配置：`scansci_pdf_elsevier_setup(api_key="YOUR_KEY", inst_token="YOUR_TOKEN")`

配置后下载 ScienceDirect 论文会优先走官方 API。

## Tor 匿名代理

Sci-Hub/LibGen 被网络封锁时使用：

```
tor_install()                    # 下载安装 Tor Expert Bundle (~30MB)
tor_start()                      # 启动 SOCKS5 代理
tor_start(use_bridges=true)      # 网络受限时用网桥
tor_stop()                       # 停止
```

`smart_download` 自动启用 Tor，无需传参。

## 故障排查

1. `scansci_pdf_network_diagnose()` — 一键诊断 DNS/代理/Tor 等
2. `scansci_pdf_health_check(detailed=true)` — 所有来源健康度 + 延迟
3. `scansci_pdf_config_get()` — 查看当前配置
4. `scansci_pdf_config_set(key="KEY", value="VALUE")` — 修改配置
5. `scansci_pdf_cache_clear()` — 清空下载缓存

### CLI 诊断命令（零 token 开销）

```bash
scansci-pdf check                  # 依赖检查
scansci-pdf config-cmd             # 查看/修改配置
scansci-pdf browser-doctor         # 浏览器运行时诊断
```

### 常见配置项

| 配置项 | 默认值 | 说明 |
|--------|-------|------|
| `output_dir` | `~/.scansci-pdf/papers` | 保存目录 |
| `scihub_enabled` | `true` | 启用 Sci-Hub 来源 |
| `network_proxy` | 空 | HTTP/SOCKS 代理 |
| `batch_workers` | `10` | 批量下载并发数 |
| `browser_headless` | `false` | 浏览器无头模式 |

## 边界情况

| 场景 | 处理方式 |
|------|---------|
| 用户只给了标题（无 DOI） | `scansci_pdf_search(标题)` → 用户选 → `download` |
| 论文不在 OpenAlex | 降级到 IEEE Xplore 直接 API / OpenAlex 原始 API / 出版商搜索（见下文排查流程） |
| 网络封锁 Sci-Hub | 配置代理 或 `config_set(scihub_enabled=false)` |
| 缺 CloakBrowser | `pip install "scansci-pdf[cloakbrowser]"` |
| 环境异常 | `setup_check()` → 按返回建议修复 |
| **中文期刊论文（振动与冲击/振动工程学报/太阳能学报等）** | 从摘要页提取 `<meta name="citation_pdf_url">` 标签（详见 `references/chinese-journal-pdf-url.md`） |

## 论文搜索失败时的排查流程

当 `scansci-pdf search` 返回空（或结果不匹配），但用户坚持论文存在时，**不要直接告诉用户"论文不存在"**。OpenAlex 有 1-6 个月的索引延迟，大量 IEEE / Elsevier 2024+ 论文不在其中。按以下顺序降级排查：

### 第一步：IEEE Xplore 直接 API 搜索

scansci-pdf 的 search 底层依赖 OpenAlex，而 IEEE Xplore 的论文索引最全。用 REST API 直接查询：

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Referer: https://ieeexplore.ieee.org/" \
  -H "Origin: https://ieeexplore.ieee.org" \
  -d '{"queryText":"YOUR_QUERY","pageNumber":1,"rowsPerPage":10,"returnFacets":["ALL"]}' \
  "https://ieeexplore.ieee.org/rest/search"
```

返回 `records` 数组，每个元素有 `articleTitle`, `doi`, `authors`, `publicationYear`, `publicationTitle`。返回空数组 = 论文确实不在 IEEE Xplore 中。此 API 无需认证。

### 第二步：OpenAlex 原始 API（更灵活）

scansci-pdf 的 search 对 OpenAlex 的查询参数做了简化。用原始 API 可以做更灵活的搜索：

```bash
# 按标题/摘要关键词搜索
curl -s "https://api.openalex.org/works?filter=title_and_abstract.search:KEYWORD,publication_year:2024&per_page=10"
# 按作者名 + 主题搜索
curl -s "https://api.openalex.org/works?filter=authorships.author.display_name.search:CHEN,title_and_abstract.search:ECAPA,publication_year:2024&per_page=10"
```

### 第三步：Crossref + Semantic Scholar 兜底

```bash
curl -s "https://api.crossref.org/works?query=ENCODED_QUERY&rows=5"
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=ENCODED_QUERY&limit=5&fields=title,year,externalIds,venue"
```

### 第四步：Web 搜索验证

DuckDuckGo 搜索精确标题：
```python
from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text('"exact paper title"', max_results=5))
```

### 第五步：生成排查报告

所有途径都返回空后，向用户输出结构化报告，包含已查数据库、各库结果、可能原因（标题有出入 / 论文刚被接收尚未上线 / 非 IEEE 期刊）和下一步需要用户提供的信息（DOI / 链接 / 作者全名）。

> **参考文件**：`references/ieee-xplore-api-search.md` — IEEE Xplore REST API 详细参数与响应格式  \
> `references/openalex-api-search.md` — OpenAlex 原始 API 多条件组合查询模式  \
> `references/publisher-cdn-patterns.md` — 出版商 CDN 直链模式（MDPI mdpi-res.com、Nature、PMC 等），用于主站被 CDN 封堵时的替代下载  \
> `references/chinese-journal-pdf-url.md` — 中文期刊（振动与冲击/振动工程学报/太阳能学报等）PDF 下载技巧，通过 `citation_pdf_url` 元标签提取 PDF 链接

## 首次使用

```bash
# CLI 一键检查
scansci-pdf check

# 或 MCP 工具
scansci_pdf_auto_setup()

# 下载第一篇试试
scansci_pdf_smart_download(identifier="10.1038/nature12373")
```

## 输出目录

下载的 PDF 默认保存在 `~/.scansci-pdf/papers/`，可通过 `config_set(key="output_dir", value="/your/path")` 修改。

---

## 已知坑 & 修复

### v1.6.1 缺少 is_suspicious_pdf 函数

Bug：`scansci_pdf/sources/__init__.py` 导入了 `is_suspicious_pdf` 和 `suspicious_pdf`，但 `pdf_utils.py` 中没有这两个函数。

修复方法：在 `pdf_utils.py` 末尾添加：

```python
def is_suspicious_pdf(path: Path) -> bool:
    try:
        size = path.stat().st_size
        if size < 50_000:
            return True
        head = path.read_bytes()[:2048].decode("utf-8", errors="replace")
        for marker in ("captcha", "verify you are human", "access denied"):
            if marker in head.lower():
                return True
        return False
    except (OSError, IOError):
        return False

def suspicious_pdf(doi: str, path: Path, source: str) -> dict:
    return {"success": False, "doi": doi, "file": str(path), "source": source, "error_type": "suspicious_pdf"}
```

### Tor 在受限网络环境

在中国网络下 `dist.torproject.org` 被墙，scansci-pdf 内置 Tor 下载会失败并反复重试。解决方案：

```bash
apt-get install tor -y                    # 安装系统 Tor
tor --SocksPort 19050 --RunAsDaemon 1      # 启动为 SOCKS5 代理
scansci-pdf config-cmd network_proxy socks5://127.0.0.1:19050  # 配置代理
```

### 论文搜索不到（OpenAlex 未索引）

scansci-pdf 的 search 命令底层依赖 OpenAlex。IEEE / Elsevier 2024 年后的新论文经常有 1-6 个月的索引延迟。不要因此断定"论文不存在"——用上述"论文搜索失败时的排查流程"降级到出版商 API 直接查询。

### IEEE / Elsevier 付费论文

大部分 IEEE 论文是闭源的。对这类论文，优先尝试：
1. OpenAlex 查 `open_access.oa_url` → arXiv 预印本（详见 `references/oa-download-fallback.md`）
2. `scansci_pdf_login(identifier="DOI")` → 浏览器机构 SSO 登录
3. CARSI 机构登录（中国高校用户，详见 `references/chinese-university-access.md`）
4. 配置 Elsevier API Key 加速 ScienceDirect 下载
