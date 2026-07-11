---
name: baidu-stealth-search
description: "Search Chinese content using stealth browser techniques (puppeteer + system Chromium), with fallback to curl for 360搜索, Sogou, and browser+cookie for Zhihu. Baidu requires proxy and still often blocked by CAPTCHA - prefer 360搜索 as primary."
version: 1.1.0
author: hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [search, baidu, chinese, stealth, proxy]
    related_skills: [duckduckgo-search, web-access]
---

# Baidu Stealth Search

Search Chinese content via Baidu, bypassing CAPTCHA detection using puppeteer-extra with stealth plugin + domestic proxy.

## Prerequisites

### Chromium

在中文服务器上用腾讯云 apt 镜像安装（快）：

```bash
# 1. 换源
cat > /etc/apt/sources.list << 'APT'
deb https://mirrors.tencent.com/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tencent.com/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tencent.com/ubuntu/ jammy-security main restricted universe multiverse
APT
apt-get update -qq

# 2. 安装 chromium
apt-get install -y chromium-browser

# 3. 验证
chromium-browser --version
# → Chromium 148.0.7778.167 snap
```

安装后路径为 `/usr/bin/chromium-browser`。

### Node + Puppeteer

```bash
# 用 cnpm（淘宝镜像，在中国很快）
npm install -g cnpm

PUPPETEER_SKIP_DOWNLOAD=true cnpm install -g puppeteer \
  puppeteer-extra puppeteer-extra-plugin-stealth \
  puppeteer-extra-plugin-user-preferences \
  puppeteer-extra-plugin-user-data-dir

# puppeteer-extra 会自动探测系统中所有插件 -> 必须在全局安装全部，否则启动时抛 ERR_MODULE_NOT_FOUND
```

注意：`puppeteer-extra` 的 `resolvePluginDependencies()` 会扫描 `require()` 树中的插件。**即使你没 `require()` 某个插件，只要它在全局 node_modules 中存在部分依赖，就会报错。** 建议优先用原生 `puppeteer` 而非 `puppeteer-extra`——对中文搜索来说 stealth 插件的额外价值有限（知乎靠 Cookie 认证而非指纹，360搜索无反爬）。

## Usage / 实战场景

根据目标平台选择策略：

### 360搜索（首选，curl 直接可用）

反爬最宽松，**无需 Cookie 和浏览器**即可用 curl 获取结果。做中文搜索的首选。

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "https://www.so.com/s?q=$(python3 -c 'import urllib.parse; print(urllib.parse.quote(\"关键词\"))')"
```

解析见 `references/curl-search-examples.md`。

### 知乎（需 Cookie）

知乎的搜索需要认证 Cookie，有两种方案：

**方案 A — Puppeteer 浏览器（推荐，稳定）**
1. 用户提供 Cookie（完整 cookie 字符串或 `z_c0=...` 值，从浏览器开发者工具 → Application → Cookies → zhihu.com 复制）
2. puppeteer 启动 Chromium，`page.setCookie()` 设置登录态
3. 访问 `https://www.zhihu.com/search?type=content&q=关键词`
4. 等待搜索结果渲染后提取标题、链接、摘要

示例脚本见 `scripts/zhihu-browser-search.js`。

**方案 B — Python API 轻量版（需 `sn-search-social-cn` 技能）**
通过知乎内部 API 配合正确 Headers + Cookie 搜索，无需 Chromium：
```bash
ZHIHU_COOKIE="完整cookie" python3 ~/.hermes/skills/sn-search-social-cn/scripts/zhihu_search.py "关键词"
```

> ⚠️ 两种方案共有：**answer 详情页面**（`/answer/xxx`）有额外反爬，即使浏览器+ Cookie 也返回 403。搜索列表页的结果摘要通常已足够。

### 百度搜索（最困难）

百度即使在浏览器中也会弹出图形验证码（h5验证/滑块验证），puppeteer 无法自动通过：
- **curl + Cookie** → 短暂可用后 CAPTCHA
- **puppeteer-extra + stealth** → 仍被拦截（百度使用行为分析 + IP信誉度）
- **结论**：百度在中文服务器上反爬级别最高，投入产出比最低。优先用 360搜索。

### 搜狗搜索（备用）

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.sogou.com/web?query=关键词"
```

结果链接多为微信文章跳转，需二次解析。

## Puppeteer 通用模式（跨平台适用）

无论目标平台（知乎、360、搜狗），用 puppeteer + 系统 Chromium 的标准模式：

```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch({
  executablePath: '/usr/bin/chromium-browser',   // ← apt 安装的系统 Chromium
  headless: 'new',                                 // 或 true（依 puppeteer 版本）
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});
const page = await browser.newPage();
// 设置 Cookie 后访问目标页
await page.setCookie(...cookies);
await page.goto(url, { waitUntil: 'networkidle2' });
// 提取结果
const results = await page.evaluate(() => {...});
```

## How it works

1. Launches Chromium via puppeteer-extra with stealth plugin
2. Routes through domestic proxy (10.126.126.1:8888) for Chinese IP
3. Sends Chinese-language headers
4. Navigates directly to `https://www.baidu.com/s?wd=...`
5. Extracts result titles, URLs, and summaries from the rendered page
6. Outputs JSON: `{keyword, resultCount, results: [{title, url, summary}]}`

## Stealth measures that bypass Baidu

| Detection vector | Normal headless Chrome | Stealth + this script |
|-----------------|----------------------|----------------------|
| navigator.webdriver | true | false |
| navigator.plugins.length | 0 | 5 |
| User-Agent | HeadlessChrome | Windows Chrome |
| Languages | en-US | zh-CN |
| IP/Geo | Singapore datacenter | Beijing Alibaba Cloud |

## Fallbacks (when Chromium / proxy not available)

本技能依赖 puppeteer + Chromium + 国内代理，三者缺一不可。如果任一条件不满足，直接换用以下替代方案。

### 替代方案 A：360搜索（推荐，curl 直接可用）

360搜索 (so.com) 反爬最宽松，无需Cookie和浏览器即可用curl搜索中文内容。做中文搜索的首选。

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.so.com/s?q=URL编码的搜索词" | python3 -c "
import sys, re, html
content = sys.stdin.read()
results = re.findall(r'<h3[^>]*>(.*?)</h3>', content, re.DOTALL)
for r in results[:12]:
    title_m = re.search(r'>\s*(.*?)\s*</a>', r)
    url_m = re.search(r'href=\"(https?://[^\"]+)\"', r)
    title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1))) if title_m else ''
    url = url_m.group(1) if url_m else ''
    if title and sum(1 for c in title if '\u4e00' <= c <= '\u9fff') >= 3:
        print(f'{title.strip()[:100]}\n  {url}\n')
"
```

### 替代方案 B：搜狗搜索（部分可用）

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.sogou.com/web?query=关键词"
```

### 替代方案 C：百度搜索（Cookie + 浏览器UA，偶有CAPTCHA）

```bash
curl -c /tmp/baidu_cookies.txt -H "User-Agent: ..." "https://www.baidu.com/" -o /dev/null
curl -sL -b /tmp/baidu_cookies.txt -H "User-Agent: ..." "https://www.baidu.com/s?wd=关键词"
```

### 策略优先级

| 优先级 | 引擎 | curl可用 | 可靠性 | 适用场景 |
|--------|------|----------|--------|----------|
| 1 | 360搜索 so.com | 稳定 | 高 | 所有中文搜索首选 |
| 2 | 搜狗 sogou.com | 微信跳转 | 中 | 补充发现 |
| 3 | 百度 baidu.com | 偶发CAPTCHA | 低 | 360不够用时 |
| 4 | 本技能 | 需puppeteer | 低 | 需要浏览器渲染时 |

详细反爬模式见 web-access skill 的 references/chinese-platform-patterns.md。

## Pitfalls

- **Baidu 即使浏览器 + stealth 也出图形验证码**：h5 验证码需要肉眼识别，puppeteer 不能自动通过。不是配置问题，是平台策略问题。
- **知乎需要用户提供 Cookie**：puppeteer 不能自动获取用户的登录态。必须用户在浏览器中手动导出 `z_c0` 值。
- **知乎 answer 详情页面有二次反爬**：`/answer/xxx` 页面经常返回 403 即使在浏览器中；搜索列表页无此问题。
- **puppeteer-extra 的插件依赖链问题**：`puppeteer-extra-plugin-user-preferences` 和 `puppeteer-extra-plugin-user-data-dir` 必须同时安装；若只有部分安装，`resolvePluginDependencies()` 在启动时会报不存在的插件未满足依赖。
- **Chromium 来源**：puppeteer 的自带 Chromium 在中国下载极慢（googleapis.com 被墙）。代替方案：
  1. `apt install chromium-browser`（推荐，腾讯/阿里镜像快）
  2. `PUPPETEER_SKIP_DOWNLOAD=true npm install puppeteer` 后通过 `executablePath` 指向系统 Chromium
- **内存占用**：每个 puppeteer 实例 ~200MB，不要同时开多个。
- **`headless: 'new'` vs `headless: true`**：取决于 puppeteer 版本。`'new'` 在 puppeteer v22+ 中已弃用，降级到 `true`。
- **Cookie 过期**：知乎 Cookie `z_c0` 有效期约 7 天，过期后返回 401。
- **360搜索的反爬容忍是特例，不是常态**：不要期望其他中文平台（如百度、小红书、抖音）也能直接用 curl 绕过。
- **中国大陆云服务器不等于无障碍访问**：百度、知乎等平台的反爬与服务器地域无关——全国内服务器 curl 同样被 405/CAPTCHA 拦截。代码审核前通过时序或用户响应得到详细结论。