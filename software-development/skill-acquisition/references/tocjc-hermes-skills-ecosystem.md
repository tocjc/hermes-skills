# tocjc/hermes-skills 生态参考

> 用户 陈冀川 的自定义技能源。Tap 已注册，技能已本地安装。
> 最新安装批次：64 个新技能，总计 **190 技能**。
> 仓库：https://github.com/tocjc/hermes-skills

## 技能全景（190 个技能）

### SN 深度研究系列（24个）

| 技能 | 依赖 | 用途 |
|------|------|------|
| `sn-deep-research` | 8 个子 skill | 深度调研编排器（规划→取证→综合→成稿） |
| `sn-research-planning` | — | 生成 plan.json，定界+维度拆解+搜索策略 |
| `sn-dimension-research` | — | 单维度执行，多轮搜索+证据筛选+交叉验证 |
| `sn-research-synthesis` | 所有子报告 | 跨维度综合，产出 synthesis.md |
| `sn-research-report` | synthesis.md | 写入 report.md 终稿 |
| `sn-report-format-discovery` | — | 报告类型结构规范发现 |
| `sn-search-academic` | — | ArXiv, Semantic Scholar, PubMed, Wikipedia |
| `sn-search-code` | — | GitHub, Stack Overflow, HN, HuggingFace |
| `sn-search-social-cn` | — | B站, 知乎, 抖音 |
| `sn-search-social-en` | — | Reddit, Twitter/X, YouTube |
| `sn-ppt-entry` | sn-ppt-creative/standard | PPT 生成入口 |
| `sn-ppt-creative` | sn-image-base | 创意模式 16:9 PPT |
| `sn-ppt-standard` | sn-image-base | 标准模式 PPT |
| `sn-ppt-doctor` | — | PPT 环境诊断 |
| `sn-image-base` | — | 底层 API（图像生成/VLM/LLM） |
| `sn-image-doctor` | — | 图像环境诊断 |
| `sn-image-imitate` | sn-image-base | 参照风格生成新图 |
| `sn-image-resume` | sn-image-base | 生成简历图 |
| `sn-infographic` | sn-image-base | 生成专业信息图 |
| `sn-md-to-html-report` | — | MD 转 HTML 长报告 |
| `sn-da-image-caption` | vision 模型 | 图片理解+数据提取 |
| `sn-da-large-file-analysis` | — | 万行以上 Excel 高性能分析 |
| `sn-da-excel-workflow` | 上述两个 + 44 子 skill | Excel 数据分析编排器 |
| `sn-update` | — | 更新 sn-* 技能集 |

### 学术论文管线（新增，5个）

| 技能 | 依赖 | 用途 |
|------|------|------|
| `academic-deep-research` | academic-shared | 深度学术研究团队（14 agent） |
| `academic-paper` | academic-shared | 论文写作管线（12 agent，10 模式） |
| `academic-paper-reviewer` | academic-shared | 多角度论文审稿（6 agent） |
| `academic-pipeline` | academic-shared | 全流程编排器（研究→写作→审稿→发表） |
| `academic-shared` | — | 共享协议/契约/契约/参考 |

**依赖链：** 上述 4 个技能均依赖 `academic-shared`。academic-shared 包含 contracts/（passport/audit/evaluator/reviewer 的 JSON Schema）、agents/（compliance_agent）、references/（firm_rules, MODE_REGISTRY）等共享层。

### Nature/CNS 论文工作流（新增，13个）

| 技能 | 用途 | 附属文件 |
|------|------|---------|
| `nature-academic-search` | 多源学术搜索（ArXiv, PubMed, Scopus 等）+ MCP server | mcp-server/, references/, scripts/ |
| `nature-citation` | 引用合规与格式（RIS/BibTeX） | references/, scripts/ |
| `nature-data` | Data Availability Statement 生成 | agents/, references/ |
| `nature-figure` | 投稿级图表 pipeline（Python/R） | assets/, evals/, references/ |
| `nature-paper2ppt` | 论文转 16:9 PPTX | references/, static/fragments/ |
| `nature-polishing` | 润色/重述/中译英/章节级打磨 | static/fragments/journal/, language/, section/ |
| `nature-reader` | 中英对照论文阅读器 | static/fragments/source/（DOI/HTML/PDF/扫描件） |
| `nature-response` | 审稿意见逐条回复 | examples/, references/, tests/ |
| `nature-reviewer` | Nature 风格审稿评估 | references/ |
| `nature-writing` | 论文各章节写作（abstract/intro/method/conclusion） | agents/, references/examples/, static/fragments/ |

**串联管线：** nature-academic-search → nature-reader → nature-writing → nature-polishing → nature-response → nature-citation → nature-data → nature-figure → nature-paper2ppt

### 实用工具（新增，6个）

`baidu-stealth-search` · `chinese-invoice-verification` · `hermes-admin` · `import-external-skills`

### sn-da-excel-workflow 子技能目录（44个）

编排器 `sn-da-excel-workflow` 按需调度以下 44 个子技能，按能力域分组：

```
sn-da-excel-workflow/
  capability/
    excel-reading/           (7)  大文件/多文件/多Sheet/范围/单Sheet/特定Sheet/结构化表头
    excel-data-cleaning/     (6)  无效数据/缺失值/数值格式/异常值/文本/重复
    excel-data-statistics/   (4)  基础统计/分类统计/分组统计/百分比
    excel-data-analysis/     (6)  比较/分组/KPI/透视表/时间序列/趋势
    excel-data-visualization/(6)  柱状图/直方图/折线图/饼图/散点图/堆叠图
    excel-data-filtering/    (4)  分类/条件/范围/阈值
    excel-cell-coloring/     (5)  分类着色/重复值/离群值/阈值/TOP值
    excel-conditional-formatting/ (1) 数据条
    excel-table-styling/     (1)  表格主题
    excel-result-export/     (4)  嵌入图表/格式化/报告/单Sheet导出
```

### 金融（3个）
`excel-author` · `pptx-author` · `stocks`

### 研究增强（6个）
`bid-analysis` · `duckduckgo-search` · `parallel-cli` · `searxng-search` · `web-access` · `scipy-signal-processing`

### 其他（5个）
`writing-beats` · `skill-eval` · `self-improving-agent` · `import-external-skills` · `hermes-admin`

## 依赖链图

```
academic-deep-research / academic-paper / academic-paper-reviewer / academic-pipeline
  └── academic-shared (contracts/, agents/compliance, references/)


nature-academic-search → nature-reader → nature-writing
  └─→ nature-polishing → nature-response → nature-citation
       └─→ nature-data → nature-figure → nature-paper2ppt


sn-deep-research
  ├── sn-research-planning
  │     └── sn-report-format-discovery (可选)
  ├── sn-dimension-research (每个维度)
  │     ├── sn-search-academic
  │     ├── sn-search-code
  │     ├── sn-search-social-cn
  │     └── sn-search-social-en
  ├── sn-research-synthesis
  └── sn-research-report

sn-ppt-entry
  ├── sn-ppt-doctor (诊断)
  ├── sn-ppt-creative (创意模式)
  │     └── sn-image-base
  └── sn-ppt-standard (标准模式)
        └── sn-image-base

sn-da-excel-workflow → 44 个子 skill（按需加载）
```

## 环境注意事项

### GitHub 代理配置

本环境设置了 `git config --global url."https://mirror.ghproxy.com/https://github.com".insteadOf "https://github.com"`
——即所有 `https://github.com/` 的 git 操作被透明代理到 ghproxy.com 镜像。

**影响：**
- `git clone` 可能因 ghproxy 超时而失败（尤其是从中国境外访问）
- 可以用 `raw.githubusercontent.com` 绕过代理直接下载文件
- GitHub REST API (`api.github.com`) 不受该代理影响，可正常工作

**实验验证：** `raw.githubusercontent.com` 在本环境可用，`github.com` 通过 git 操作不可用。
