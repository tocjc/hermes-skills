---
name: patent-disclosure
description: "通用中国专利挖掘发现与交底书生成全流程：扫描项目文档挖掘专利点、讨论融合、基于脱敏模版生成技术交底书、联网查新、生成后自检含逻辑闭环与公式参数一致性。| Patent mining, disclosure drafting, prior-art search, and consistency self-check."
version: "1.0.0"
author: "handsomestWei → adapted for Hermes Agent"
---

# 专利挖掘与交底书生成

本技能覆盖 **专利点挖掘** → **查新与差异化** → **交底书生成** → **自检完善** 全流程；分步指令在 **prompts/** 目录下，每步执行前请 `read_file` 对应文件。

## 环境与约定

- **语言**：默认与用户语种一致；专利与法律术语采用行业常用表述。
- **图示定稿**：**3.2 系统框图** / **3.4 流程图** 用 fenced **mermaid** 代码块；定稿时用 `tools/mermaid_render.py` 转 PNG + 生成 Word。详见 `tools/README.md`。

## 触发条件

以下任一方式启用本技能：

- 用户明确提及：专利挖掘、专利点、技术交底书、交底书、专利交底书、查新、现有技术对比等
- **迭代模式（按意图识别）**：当用户意图明显是在**已有交底书或上一轮输出**上继续工作（改章节、补实施例、补材料、修正参数/事实、调整表述等），**无需**用户说出「迭代」等固定词——直接 `read_file` `prompts/iteration_context.md`，再根据意图选用 `prompts/merger.md`（新材料/扩展合并）或 `prompts/correction_handler.md`（纠错/事实不符），**另存为新文件** `{案件名}_{YYYYMMDDHHmmss}.md` 与同名 `.docx`，**不覆盖**旧稿。**禁止**在迭代意图已成立时默认回到 Step 3–4 专利点全文分析（除非用户明确要求重新挖掘）。

## 依赖安装

```bash
# 基础依赖（文档转换、mermaid 渲染、公式、Word 输出）
pip install -r <技能目录>/tools/requirements.txt

# 国知局查新（Step 5 优先渠道）
pip install -r <技能目录>/tools/requirements-cnipa.txt
python -m playwright install chromium

# mermaid CLI（系统级依赖，Node.js 须已安装）
cd <技能目录>/tools && npm install
```

## 工具与数据来源

| 任务 | 建议方式 |
|------|----------|
| 加载分步指令 | `read_file` → `prompts/*.md`（见下表） |
| 读代码、设计文档、PDF、图片 | `read_file`、`vision_analyze`；大仓库先用 `search_files` 定位再精读 |
| Word（.docx）→ Markdown | `terminal` → `python3 <skill_dir>/tools/docx_to_md.py --input {path}.docx --output {dir}/{name}.md` |
| PowerPoint（.pptx）→ Markdown | `terminal` → `python3 <skill_dir>/tools/pptx_to_md.py --input {path}.pptx --output {dir}/{name}.md` |
| 联网查新（Step 5） | 优先 `tools/cnipa_epub_search.py`（**分多次调用、每轮一词**，自行合并 `EPUB_HITS_JSON`）；降级用 `web_search`（Google 学术/Google Patents） |
| 交底书定稿交付（**须同时** .md + .docx） | `terminal` → `python3 <skill_dir>/tools/mermaid_render.py -i draft.md -o "{案件名}_{YYYYMMDDHHmmss}.md"` |
| 保存输出路径 | `outputs/{案件标识}/`；文件名一律 `{案件名}_{YYYYMMDDHHmmss}`（含首次定稿与迭代），见 `disclosure_builder.md §7.3` |
| 迭代对话留档 | 每轮交付后在案件目录追加 `交底书修订对话记录.md`（用 `tools/iteration_dialog_log.py` 或手工） |

> **注意**：`<skill_dir>` 是技能安装目录，Hermes 中可通过 `skill_view(name='patent-disclosure')` 获取 `skill_dir` 路径。

## Prompt 文件映射（执行指引）

| 步骤 | 文件 | 用途 |
|------|------|------|
| Step 1 | `prompts/intake.md` | 边界与输入问题 |
| Step 2 | `prompts/project_scan.md` | 项目文档扫描；**须**对 `.docx`/`.pptx` 先转换再读 |
| Step 3–4 | `prompts/patent_points_analyzer.md` | 候选专利点、融合与选定 |
| Step 5 | `prompts/prior_art_search.md` | 联网查新与分析要求 |
| Step 6 | `prompts/disclosure_preview.md` | 全文前的摘要预览 |
| Step 7 | `prompts/disclosure_builder.md` + `prompts/template_reference.md` | 交底书结构、脱敏、符号与公式体例、图示规范 |
| Step 8 | `prompts/disclosure_self_check.md` | 内部自检，不写入正文 |
| 迭代 | `prompts/iteration_context.md` | 迭代意图识别、落盘命名、修订对话记录 |
| 迭代 | `prompts/merger.md` | 新材料增量合并；输出 `{案件名}_{时间戳}.md`/`.docx` |
| 迭代 | `prompts/correction_handler.md` | 对话纠正；输出 `{案件名}_{时间戳}.md`/`.docx` |

## 主流程执行顺序

1. **`read_file` `prompts/intake.md`** → 执行 Step 1
2. **`read_file` `prompts/project_scan.md`** → 执行 Step 2（扫描文档，含 Office 转换）
3. **`read_file` `prompts/patent_points_analyzer.md`** → 执行 Step 3–4（挖掘并选定专利点）
4. **`read_file` `prompts/prior_art_search.md`** → 执行 Step 5（查新检索）
5. **`read_file` `prompts/disclosure_preview.md`** → 执行 Step 6（摘要预览，用户可跳过）
6. **`read_file` `prompts/disclosure_builder.md`** + **`read_file` `prompts/template_reference.md`** → 执行 Step 7（生成交底书全文，含 mermaid 图示 + 权利要求偏向点建议）
7. **`read_file` `prompts/disclosure_self_check.md`** → 内部执行 Step 8，修订后交付

## 迭代模式

**启用**：根据用户自然语言意图判断，不需固定关键词。

**补充材料/扩展章节**或 **§7.6 第五章权利要求书式强化**：
1. `read_file` `prompts/iteration_context.md` → `read_file` `prompts/merger.md`
2. 合并结果**另存为**带时间戳的 `.md`/`.docx`
3. **追加** `交底书修订对话记录.md`
4. 输出「合并摘要」留档

**指出错误/与事实不符**：
1. `read_file` `prompts/iteration_context.md` → `read_file` `prompts/correction_handler.md`
2. 纠正结果**另存为**带时间戳的 `.md`/`.docx`
3. **追加**对话记录
4. 输出「纠正摘要」留档

## Agent 自用检查清单

- [ ] 已按步骤 `read_file` 对应 prompts；Step 2 若含 Office 文档，已先转换再读
- [ ] 识别到「在已有交底书上修改」时，已走迭代路径（`iteration_context.md` + `merger.md` / `correction_handler.md`），交付为**新时间戳文件**
- [ ] 执行 merger/correction 后已输出留档摘要，案件目录已追加 `交底书修订对话记录.md`
- [ ] 查新完成并写入 1.1 与区别论述（优先 `tools/cnipa_epub_search.py`，分多次调用、自行合并 JSON；`abstract` 必用）
- [ ] 脱敏、mermaid 已渲染 PNG、章节引用符合 template_reference；已交付 `.md` + `.docx`
- [ ] 定稿对话已含 `disclosure_builder.md §7.6`「权利要求偏向点」建议（不入正文、不捏造）
- [ ] 自检在后台完成，正文无自检清单章节、无技能仓库脚注