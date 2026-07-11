# 中文期刊 PDF 下载指南

## 核心技巧：`citation_pdf_url` meta 标签

绝大多数中文期刊网站（CNKI 除外）在摘要页的 HTML 中嵌入 `<meta name="citation_pdf_url">` 标签，指向 PDF 文件。这比找页面上的"PDF下载"链接更可靠——页面可能 JS 渲染，但 meta 标签在原始 HTML 中。

通用流程：

```bash
# 1. 访问摘要页
html=$(curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "$ABSTRACT_URL")

# 2. 提取 PDF 链接
pdf_url=$(echo "$html" | grep -oP 'citation_pdf_url[^>]*content="\K[^"]+')

# 3. 下载
curl -sL "$pdf_url" -o paper.pdf
```

## 已验证的期刊

| 期刊 | 网站 | PDF URL 模式 | 已验证 |
|------|------|-------------|--------|
| 振动与冲击 | `jvs.sjtu.edu.cn` | `{CN\|EN}/PDF/{article_id}` | ✅ 12/12 |
| 振动工程学报 | `pubs.cstam.org.cn` | `data/article/zdgcxb/preview/pdf/...pdf` | ✅ 2/2 |
| 太阳能学报 | `www.tynxb.org.cn` | `CN/PDF/10.19912/j.0254-0096.tynxb.20xx-xxxx` | ✅ 2/2 |

## 已知问题

### CNKI（知网）
CNKI 的页面不嵌入 `citation_pdf_url` 标签。PDF 下载需要登录态或机构访问。CNKI 论文目前只能通过浏览器 + 机构登录获取。

### 部分期刊使用 JS 动态加载
少数期刊（如《机械工程学报》）的 PDF 链接通过 AJAX 动态加载，meta 标签可能指向 HTML 页面而非 PDF。此时需要：
1. 用 `browser_navigate` 访问摘要页
2. 用 `browser_console` 执行 JS 提取下载链接
3. 或使用 `browser_vision` 截图识别下载按钮

### 反爬限制
- 高频请求触发 CAPTCHA（尤其 jvs.sjtu.edu.cn）
- 建议请求间加 1-2 秒延迟
- 使用 `curl -sL` 并带完整 Chrome User-Agent 头