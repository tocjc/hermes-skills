---
name: sn-search-social-cn
description: 搜索中文社交平台：B站视频、知乎问答、抖音视频。部分平台需要 cookie 认证，稳定性因平台而异。
---

# sn-search-social-cn - 中文社交平台搜索

搜索 B站、知乎、抖音三个中文社交平台。

## 稳定性说明

中文社交平台没有稳定的公开搜索 API，所有脚本依赖内部 API 或第三方库，**可能因平台更新而失效**。

### 不使用脚本时（curl/直接 HTTP 访问）的失败模式

注意：这些平台的访问限制来自 **反爬机制**，与服务器物理地域无关。国内云服务器同样会遇到。

| 平台 | curl 访问结果 | 原因 |
|------|-------------|------|
| 知乎 | HTTP 405 Method Not Allowed | IP/UA 级别封禁 curl |
| 微信文章 | 返回空白 DOM（`document.title = '微信公众平台'`） | 未登录态 |
| 百度搜索 | 返回 CAPTCHA 验证页 | 浏览器指纹检测 |
| Bing 中文版 | 查询词被拆成单字 | URL 编码被重写 |
| 小红书 | 需登录 + 设备指纹 | 强反爬 |
| 搜狗搜索 | 部分可用（结果多为微信跳转链接） | 反爬较宽松 |

**原则**：脚本失败时，不要默认归因为"海外/网络问题"。先确认平台行为——用浏览器工具（`browser_navigate`）做交叉验证。如果脚本和浏览器都失败，才是真正的访问限制。

## 依赖

运行脚本前先安装本 skill 的 Python 依赖：

```bash
python3 -m pip install -r skills/sn-search-social-cn/requirements.txt
```

如果项目使用 `uv` 环境：

```bash
uv pip install -r skills/sn-search-social-cn/requirements.txt
```

| 脚本 | 平台 | 稳定性 | 认证方式 |
|------|------|--------|---------|
| `bilibili_search.py` | B站 | 较高 | 无需（可选 cookie 提高质量） |
| `zhihu_search.py` | 知乎 | 中等 | 需 `ZHIHU_COOKIE` |
| `douyin_search.py` | 抖音 | 较低 | 需 `DOUYIN_COOKIE` |

## Cookie 获取方式

1. 在浏览器中登录对应平台
2. 打开开发者工具（F12）→ Network 标签
3. 刷新页面，在请求头中找到 `Cookie` 字段
4. 将完整 cookie 字符串设置为对应环境变量

## 参数说明

### bilibili_search.py

```bash
python3 scripts/bilibili_search.py <query> [选项]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词（必填） | — |
| `--limit`, `-n` | 返回结果数量 | 10 |
| `--cookie` | B站 Cookie（也可通过 `BILIBILI_COOKIE` 环境变量设置，可选，提高结果质量） | — |
| `--order` | 排序：空=综合, `totalrank`=最佳匹配, `click`=播放, `pubdate`=最新, `dm`=弹幕, `stow`=收藏 | 综合 |

```bash
python3 scripts/bilibili_search.py "机器学习教程" --limit 5
python3 scripts/bilibili_search.py "Python" --order click --limit 10
```

### zhihu_search.py

```bash
python3 scripts/zhihu_search.py <query> [选项]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词（必填） | — |
| `--limit`, `-n` | 返回结果数量 | 10 |
| `--cookie` | 知乎 Cookie（也可通过 `ZHIHU_COOKIE` 环境变量设置，必填） | — |
| `--type` | 搜索类型：`general`, `topic`, `people`, `zvideo` | general |

```bash
ZHIHU_COOKIE="..." python3 scripts/zhihu_search.py "Python 异步编程" --limit 5
python3 scripts/zhihu_search.py "大模型" --cookie "..." --type topic --limit 5
```

### douyin_search.py

```bash
python3 scripts/douyin_search.py <query> [选项]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词（必填） | — |
| `--limit`, `-n` | 返回结果数量 | 10 |
| `--cookie` | 抖音 Cookie（也可通过 `DOUYIN_COOKIE` 环境变量设置，必填） | — |

```bash
DOUYIN_COOKIE="..." python3 scripts/douyin_search.py "编程教程" --limit 5
```

## 输出格式

标准 JSON：`{"success": true, "query": "...", "provider": "bilibili|zhihu|douyin", "items": [...], "error": null}`
