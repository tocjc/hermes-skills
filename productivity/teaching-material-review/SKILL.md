---
name: teaching-material-review
description: "审校教学课件/PPT: 检查文字图片准确性, 评估科学性先进性, 对比新旧版本, 输出Markdown审校报告."
---

# 教学课件审校（Teaching Material Review）

以资深学科编辑/课程教师视角，对 PPT 课件做内容准确性审校，输出带评分、修改建议和采纳追踪的结构化 Markdown 报告。

## When to Use
- 用户提供 `.pptx` 文件并要求"审校/校对/检查内容是否准确、图片内容、文字是否准确"
- 要求对每个 PPT 的内容、组织、科学性、先进性、合理性给出评价
- 用户提供"旧版 + 修订版"两套 PPT，要求对比修改情况、追踪建议采纳率
- 用户要求对需要修改的内容列出详细理由

## Workflow

### 1. 列出文件并确认存在
```bash
ls -lh /root/*.pptx      # 注意文件名可能含空格/中文，引用时加引号
```

### 2. 提取 PPT 文本、表格、图片（python-pptx）
先 `pip install python-pptx`（若缺失）。用独立脚本（避免 f-string 大括号与 shell 引号冲突，见 Pitfalls）：

```python
from pptx import Presentation
prs = Presentation(path)
for i, slide in enumerate(prs.slides):
    print(f'=== SLIDE {i+1} ===')
    print('Layout:', slide.slide_layout.name if slide.slide_layout else 'unknown')
    for shape in slide.shapes:
        st = str(shape.shape_type)
        if shape.has_text_frame:
            t = shape.text_frame.text.strip()
            if t: print(f'  [{st}] {t[:300]}')          # 换行符转 \\n 便于阅读
        if shape.has_table:
            for row in shape.table.rows:
                print('  [TABLE]', ' | '.join(c.text.strip()[:30] for c in row.cells))
        if shape.shape_type == 13:                       # Picture
            img = shape.image
            print(f'  [IMAGE] {img.content_type}, {img.size} bytes')
```

### 3. 提取图片供视觉核查
将每张图片导出为文件，用 `vision_analyze` 核查架构图/截图内容是否与图题、正文一致：
```python
for shape in slide.shapes:
    if shape.shape_type == 13:
        with open(f'{outdir}/{slide_no:02d}_{n}.{ext}', 'wb') as f:
            f.write(shape.image.blob)
```

### 4. 逐页分析（对照专业知识库）
- **科学性**：概念、定义、数据、时间线、模型描述是否准确
- **先进性**：内容是否覆盖该领域最新进展（AI 课程尤其要查 2023-2025 年里程碑，如 GPT-4o、Sora、DeepSeek-R1、Claude）
- **合理性/结构**：章节递进、篇幅、难度是否适合目标学生
- **教学性**：类比是否贴切、图文是否匹配、案例是否典型
- 图片核查：尺寸对比可快速判断旧版 vs 新版是否更换了图（同尺寸=未换，尺寸变化=已换）

### 5. 新旧版本对比（核心增值步骤）
对每项上次建议，标记状态：✅已修 / ⚠️待确认 / ❌未修。汇总采纳率：
```
| 级别 | 建议总数 | 已采纳 | 采纳率 |
| 高优先级 | 7 | 4 | 57% |
```
结论表述要明确：某 PPT 内容停留在旧年份=严重滞后（先进性打低分），某 PPT 全部采纳=进步最大。

### 6. 输出报告结构
每个 PPT 一节，含：内容概要表 → 已采纳修改表 → 未采纳建议分析（原文/问题/建议/理由）→ 评分表（科学性/先进性/结构/教学性 + 综合分）→ 结论（✅通过/⚠️补X后通过/❌建议修改后使用）。结尾附总体采纳率、仍待修改清单（按优先级）、关键意见。

## Scoring Rubric
| 维度 | 关注点 |
|------|--------|
| 科学性 | 概念/数据/时间线/模型描述准确，无原则性错误 |
| 先进性 | 覆盖领域最新进展；旧年份内容无更新 = 严重滞后（≤7.5分） |
| 合理性 | 结构递进、难度适中、图文匹配 |
| 教学性 | 类比贴切、案例典型、易理解 |

综合分建议：≥9.3 通过；9.0-9.2 补关键概念后通过；<9.0 需重大修改。修改建议按 🔴高 / 🟡中 / 🟢低 分级。

## Pitfalls
- **python-pptx 提取脚本的引号地狱**：在 `execute_code` 或 `terminal -c` 里嵌 f-string + 中文引号 + 大括号极易触发 NameError 或 shell 解析错误。**先 write_file 写成独立 .py，再 terminal 执行**，传参用 `sys.argv`。
- **vision_analyze 可能 429 限流**：批量核查图片时逐张调用，失败就放弃视觉核查，靠文本 + 图片尺寸对比做判断，不要阻塞整个审校。
- **文件名含空格/中文**（如 `10.4 改.pptx`）：shell 命令必须加引号，python 脚本用 `sys.argv[1]` 原样接收。
- **图片尺寸 = 是否更换的代理指标**：新旧版图片尺寸一致基本=未换图；尺寸变化=已换图（需再视觉确认内容）。
- **审校≠创作**：报告只指出问题+理由+建议，不替作者改写内容；"建议通过/建议修改"结论要明确。
- **AI 课程内容时效性**：2025 年课程若只提 2022 年模型（如 Make-A-Video 不提 Sora）属于严重滞后，先进性评分必须反映这一点。

## References
- `references/ai-course-ppt-review-template.md` — AI 课程课件审校的完整工作样例：评分表、建议采纳追踪表、AI 课件（生成式AI/大模型/多模态）常见问题清单。