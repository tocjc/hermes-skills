---
name: web-access
license: MIT
description: |
  所有联网操作必须通过此 skill 处理，包括：搜索、网页浏览、爬取内容、登录后操作、交互操作等。
  触发场景：用户要求搜索信息、查看网页内容、访问需要登录的网站、操作网页界面、抓取社交媒体内容、
  读取动态渲染页面、以及任何需要真实浏览器环境的网络任务。
  改编自 eze-is/web-access (v2.5.3)，适配 Hermes Agent 内置浏览器+搜索工具。
metadata:
  origin: https://github.com/eze-is/web-access
  hermes-version: "1.0"
---

# web-access Skill (Hermes Agent 版)

## 适用场景

当用户要求以下任务时，**必须**加载此 skill：

- 搜索信息、查找资料、调研某个话题
- 读取/查看某个网页、URL 内容
- 访问需要登录的网站（社交平台、内部系统等）
- 操作网页界面（表单填写、点击、登录等）
- 抓取社交媒体内容（小红书、微博、知乎、推特等）
- 读取动态渲染页面（如 SPA 单页应用）
- 对比多个网站的信息
- 任何需要联网的任务

**不适用**：纯本地文件分析、不需要网络访问的代码任务。

## 浏览哲学

**像人一样思考，兼顾高效与适应性地完成任务。**

执行任务时不要过度依赖固有印象所规划的步骤，而是带着目标进入，边看边判断，遇到阻碍就解决，发现内容不够就深入——全程围绕「我要达成什么」做决策。

### ① 拿到请求
先明确用户要做什么，定义成功标准：什么算完成了？需要获取什么信息、执行什么操作、达到什么结果？这是后续所有判断的锚点。

### ② 选择起点
根据任务性质、平台特征、达成条件，选一个最可能直达的方式作为第一步去验证。一次成功当然最好；不成功则在③中调整。

### ③ 过程校验
每一步的结果都是证据，不只是成功或失败的二元信号。用结果对照①的成功标准，更新你对目标的判断：路径在推进吗？结果的整体面貌（质量、相关度、量级）是否指向目标可达？发现方向错了立即调整，不在同一个方式上反复重试。

- 搜索没命中 ≠ "还没找对方法"，也可能是 "目标不存在"
- API 报错、页面缺少预期元素、重试无改善，都是在告诉你该重新评估方向
- 遇到弹窗、登录墙等障碍，判断它是否真的挡住了目标：挡住了就处理，没挡住就绕过——内容可能已在页面 DOM 中，交互只是展示手段

### ④ 完成判断
对照定义的任务成功标准，确认任务完成后才停止，但也不要过度操作，不为了"完整"而浪费代价。

## 联网工具选择

- **确保信息的真实性，一手信息优于二手信息**：搜索引擎和聚合平台是信息发现入口。当多次搜索尝试后没有质的改进时，升级到更根本的获取方式：定位一手来源（官网、官方平台、原始页面）。

| 场景 | Hermes 工具 |
|------|------------|
| 搜索摘要或关键词结果，发现信息来源 | **duckduckgo-search / searxng-search / web_search**（使用搜索相关 skill 或直接 web_search 工具） |
| URL 已知，需要从页面提取特定信息 | **browser_navigate + browser_snapshot**（Hermes 内置浏览器提取页面内容） |
| URL 已知，需要原始 HTML 源码（meta、JSON-LD 等结构化字段） | **terminal** 执行 `curl -sL` |
| 需要交互操作（点击、表单、滚动加载） | **browser_navigate + browser_click + browser_scroll + browser_type** |
| 需要看页面视觉渲染状态、截图 | **browser_vision**（截图 + AI 分析） |
| 非公开内容，或反爬严重的平台（小红书、微信公众号等） | **Hermes 内置浏览器**（携带登录态场景需用户配合） |
| 需要登录态 | 在浏览器中请求用户登录，登录后无需重启浏览器即可继续操作 |

### 各工具说明

**搜索与发现**：
- `duckduckgo-search` skill：免费搜索，适合英文内容发现
- `searxng-search` skill：聚合搜索引擎，适合中文内容发现
- 直接通过 Hermes web 工具集搜索（由你的 toolset 提供）

**内容提取**：
- **`browser_navigate` + `browser_snapshot`**：导航到指定 URL，获取页面快照。适合文章、博客、新闻、文档等文本为主的内容
- **browser_vision**：截图并理解页面视觉内容，适合包含图片/图表的页面，也适合需要视觉确认的场景（如验证码、弹窗、支付页面等）
- **`terminal` + `curl`**：获取原始 HTML，适合提取 JSON-LD、meta 标签等结构化数据

**交互操作**：
- `browser_snapshot`：获取当前页面的交互元素列表（带 ref ID）
- `browser_click(ref)`：通过 ref ID 点击元素
- `browser_type(ref, text)`：在输入框中输入文本
- `browser_scroll(direction)`：滚动页面
- `browser_press(key)`：按键操作（Enter、Tab 等）
- `browser_console(expression=...)`：执行 JavaScript 在页面中提取数据

> **浏览网页时，先了解页面结构，再决定下一步动作**。不需要提前规划所有步骤。

### 补充：技术事实

- Hermes 内置浏览器使用 headless 浏览器，**不是**用户的日常浏览器——默认不带用户登录态
- 当需要登录态时（访问需要登录的平台），请在打开页面后先尝试获取目标内容。只有当确认**目标内容无法获取**且判断登录能解决时，才告知用户：*"当前页面需要登录才能获取[具体内容]，请告诉我登录所需的凭证或帮你打开登录页面。"*
- 页面中存在大量已加载但未展示的内容——轮播中非当前帧的图片、折叠区块的文字、懒加载占位元素等，它们存在于 DOM 中但对用户不可见
- 通过 `browser_console(expression=...)` 可以执行 JavaScript 直接操作 DOM、提取数据
- 平台返回的"内容不存在""页面不见了"等提示不一定反映真实状态，也可能是访问方式的问题

## 并行调研：子 Agent 分治策略

任务包含多个**独立**调研目标时（如同时调研 N 个项目、N 个来源），使用 `delegate_task` 分发子 Agent 并行执行。

**好处**：
- **速度**：多子 Agent 并行，总耗时约等于单个子任务时长
- **上下文保护**：抓取内容不进入主 Agent 上下文，主 Agent 只接收摘要，节省 token

**分治判断标准**：

| 适合分治 | 不适合分治 |
|----------|-----------|
| 目标相互独立，结果互不依赖 | 目标有依赖关系，下一个需要上一个的结果 |
| 每个子任务量足够大（多页抓取、多轮搜索） | 简单单页查询，分治开销大于收益 |
| 需要浏览器或长时间运行的任务 | 几次搜索就能完成的轻量查询 |

**子 Agent Prompt 写法**：目标导向，而非步骤指令
- 主 Agent 的职责是说清楚**要什么**，仅在必要与确信时限定**怎么做**
- 过度指定步骤会剥夺子 Agent 的判断空间，反而引入主 Agent 的假设错误
- **避免用词对子 Agent 行为的暗示**：「搜索xx」会把子 Agent 锚定到搜索，而实际上有些反爬站点需要直接浏览器访问才能有效获取
- 建议描述目标（「获取」「调研」「了解」），避免用暗示具体手段的动词（「搜索」「抓取」「爬取」）

## 信息核实类任务

核实的目标是**一手来源**，而非更多的二手报道。多个媒体引用同一个错误会造成循环印证假象。

搜索引擎和聚合平台是信息发现入口，是**定位**信息的工具，不可用于直接**证明**真伪。找到来源后，直接访问读取原文。

| 信息类型 | 一手来源 |
|----------|---------|
| 政策/法规 | 发布机构官网 |
| 企业公告 | 公司官方新闻页 |
| 学术声明 | 原始论文/机构官网 |
| 工具能力/用法 | 官方文档、源码 |

**找不到官网时**：权威媒体的原创报道（非转载）可作为次级依据，但需向用户说明："未找到官方原文，以下核实来自[媒体名]报道，存在转述误差可能。" 单一来源时同样向用户声明。

## 通用浏览器操作流程

### 打开一个页面并阅读内容

```
1. browser_navigate(url) — 导航到目标 URL
2. browser_snapshot() — 获取页面快照，查看交互元素和内容概要
3. 如需更多内容 → browser_scroll(direction='down')
4. 如需分析图片/视觉内容 → browser_vision(question='...')
5. 如需提取页面上特定数据 → browser_console(expression='document.querySelectorAll(...)')
6. 如需点击链接 → browser_click(ref='@eX')
7. 如需输入文本 → browser_type(ref='@eX', text='...')
```

### 处理需要交互的页面（搜索、表单等）

```
1. browser_navigate(url) 打开页面
2. browser_snapshot() 查看可交互元素
3. browser_type(ref='@eX', text='搜索关键词') 在搜索框输入
4. browser_click(ref='@eY') 点击搜索按钮
5. browser_snapshot() 查看搜索结果
6. browser_click(ref='@eZ') 点击某个结果链接
7. 反复：snapshot → scroll → click 直到获取所需信息
```

### 提取页面中的结构化数据

```javascript
// 通过 browser_console(expression=...) 执行 JS 提取数据
// 例：提取所有链接
JSON.stringify(Array.from(document.querySelectorAll('a')).map(a => ({
  text: a.textContent.trim(),
  href: a.href
})).filter(x => x.text))

// 例：提取表格数据
JSON.stringify(Array.from(document.querySelectorAll('table')).map(table => ({
  headers: Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim()),
  rows: Array.from(table.querySelectorAll('tr')).map(row =>
    Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
  ).filter(r => r.length > 0)
})))
```

## 站点经验积累

操作中积累的特定网站经验，可以记录在技能目录下的 `references/site-patterns/` 中。

当你发现某个网站有特殊的访问约束、URL 模式、反爬行为或操作策略时，使用 `write_file` 或 `patch` 将经验记录下来。后续再次访问同一网站时先读取对应经验文件。

文件格式：
```markdown
---
domain: example.com
aliases: [示例, Example]
updated: 2026-05-26
---
## 平台特征
架构、反爬行为、登录需求、内容加载方式等事实

## 有效模式
已验证的 URL 模式、操作策略、选择器

## 已知陷阱
什么会失败以及为什么
```

经验内容标注发现日期，当作"可能有效的提示"而非"保证正确的事实"。

## ## 陷阱：不要把反爬归因为"地域/海外问题"

国内主流内容平台（知乎、百度、微信等）的反爬机制 **与服务器的物理地域无关**。国内云服务器上的 curl/脚本请求同样会被拦截（CAPTCHA、405、空DOM等）。

**错误的归因模式**：
```
❌ "知乎搜索失败是因为海外服务器访问受限"
✅ "知乎返回405，是反爬拦截——需要浏览器或Cookie"
```

**正确的诊断流程**：
1. 看响应状态码 + 内容特征（是CAPTCHA白页还是真404？）
2. 查 HERMES MEMORY 中的 `references/chinese-platform-patterns.md` 对照已知模式
3. 对应选择工具升级：curl→浏览器→登录态浏览器

> 详细平台反爬模式见：[`references/chinese-platform-patterns.md`](references/chinese-platform-patterns.md)

## 常见场景速查

### 阅读一篇公开文章/博客
```
browser_navigate → browser_snapshot → (如需滚动) browser_scroll → browser_vision(含图片时)
```

### 搜索信息并对比结果
```
1. duckduckgo-search / searxng-search 搜索
2. 对每个值得深入的结果: browser_navigate → browser_snapshot
3. 汇总对比
```

### 访问社交平台内容（小红书、微博、知乎等）
```
1. browser_navigate 打开目标链接
2. browser_snapshot 查看页面结构
3. 可能需要 browser_scroll 触发加载更多
4. 内容较多时: browser_console(expression='...') 批量提取
```

### 并行调研多个独立目标
```
delegate_task(tasks=[
  {goal: "调研 A 产品官网", context: "..."},
  {goal: "调研 B 产品官网", context: "..."},
  {goal: "调研 C 产品官网", context: "..."}
])
```

### 验证一个事实/消息的真实性
```
1. 搜索定位一手来源（官网、官方公告、原论文）
2. browser_navigate 直接访问原文
3. 提取关键信息并交叉比对
4. 向用户报告结论，说明来源可靠性
```