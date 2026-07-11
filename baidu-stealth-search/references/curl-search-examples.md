# 中文搜索 curl 使用示例

当无法使用 puppeteer/浏览器时，以下 curl 命令可直接用于中文搜索信息发现。

## 360搜索（首选，最稳定）

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "https://www.so.com/s?q=关键词URL编码" | python3 -c "
import sys, re, html
content = sys.stdin.read()
results = re.findall(r'<h3[^>]*>(.*?)</h3>', content, re.DOTALL)
for r in results[:12]:
    title_m = re.search(r'>\\s*(.*?)\\s*</a>', r)
    url_m = re.search(r'href=\\\"(https?://[^\\\"]+)\\\"', r)
    title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1))) if title_m else ''
    url = url_m.group(1) if url_m else ''
    if title and sum(1 for c in title if '\\u4e00' <= c <= '\\u9fff') >= 3:
        print(f'{title.strip()[:100]}\\n  {url}\\n')
"
```

## 搜狗搜索（备用，部分可用）

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.sogou.com/web?query=关键词"
```

结果链接多为微信文章跳转，需要二次解析。

## 百度搜索（需先获取Cookie，成功率低）

```bash
# 第一步：访问首页获取 BAIDUID Cookie
curl -c /tmp/baidu_cookies.txt \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.baidu.com/" -o /dev/null -s

# 第二步：用同一个Cookie jar搜索
curl -sL -b /tmp/baidu_cookies.txt \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "https://www.baidu.com/s?wd=关键词"
```

⚠️ 百度即使携带Cookie也经常返回CAPTCHA验证页。如果遇到，换用360搜索。

## 知乎 API 搜索（需 Cookie）

知乎有 Python 脚本可实现 API 级搜索，见本技能 `sn-search-social-cn` 的 `zhihu_search.py`：

```bash
ZHIHU_COOKIE="完整cookie字符串" python3 ~/.hermes/skills/sn-search-social-cn/scripts/zhihu_search.py "关键词" --limit 5
```

需先安装 Python 依赖：`pip install requests`（或从 `sn-search-social-cn/requirements.txt` 安装）。

## 处理结果中的重定向链接

360搜索和搜狗返回的URL是重定向链接，要访问原文需要解析。Python 方式：

```python
import requests
resp = requests.get(url, allow_redirects=True)
# 或从响应头 Location 提取最终URL
```

## 搜索结果解析速查

| 引擎 | 搜索结果容器 | 标题选择器 | 链接选择器 |
|------|-------------|-----------|-----------|
| 360搜索 | `<h3>` 标签 | `re.findall(r'<h3[^>]*>(.*?)</h3>')` | href from `<a>` in h3 |
| 搜狗搜索 | `<h3>` 标签 | 同上 | 同上，但URL多为微信跳转 |
| 百度搜索 | `<h3>` 或 `.c-container` | 同上 | need unescape + decode |
