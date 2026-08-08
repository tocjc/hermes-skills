# Technical Document Analysis & Vault Import Workflow

When the user asks to analyze a **technical/bidding document** (PDF/DOCX) and save the analysis to the knowledge base.

## Workflow

### Phase 1: Extract Text from PDF

Install pymupdf if not present:

```bash
pip install pymupdf
```

Extract all pages:

```python
import pymupdf
doc = pymupdf.open('/path/to/file.pdf')
for page in doc:
    print(page.get_text())
```

For large PDFs, extract specific pages or use offset/limit to manage context.

### Phase 2: Analyze the Document

For each document type, use the appropriate analysis template:

#### A. Technical Requirements / Task Document (任务书/需求书)

Focus on:
- **Core scope**: project name, hardware platform, data scale, timeline
- **Functional modules**: list each module with requirements
- **Constraints**: budget, team size, IP, security, 国产化
- **Acceptance criteria**: what defines "done", quantifiable metrics
- **Risk assessment**: identify 8+ risks with severity ratings (高风险/中风险/低风险)
- **Recommendations**: actionable negotiation points before signing

Output template:

```
## 项目概况
## 一、核心内容
## 二、研究目标（共N项）
## 三、工作要求
## 四、验收要求
## 五、风险分析与预警（N项）
## 六、综合建议
```

#### B. Technical Proposal / Bidding Document (技术方案/投标文件)

Focus on:
- **Module decomposition**: break the system into modules
- **Technology comparison**: 3+ options per module with trade-off table
- **Architecture design**: Mermaid diagram of data flow + module dependencies
- **Workload estimation**: person-days per module, team composition
- **Cost estimation**: direct labor + infrastructure + overhead + risk reserve
- **Timeline**: phased delivery with Gantt-style chart
- **Risk assessment**: technical risks, schedule risks, dependency risks

Output template:

```
## 项目概况
## 一、逐项开发内容、难点与工作量评估
## 二、开发费用评估
## 三、人力安排
## 四、开发周期
## 五、风险提示
```

#### C. Code Review / Model Optimization Analysis

Focus on:
- **Script overview**: framework, architecture, data flow
- **Bug classification**: P0 (crash/wrong results), P1 (logic defects), P2 (optimization)
- **Architecture issues**: model depth, missing components (BN, dropout, residual)
- **Training strategy**: lr schedule, data augmentation, early stopping, gradient clipping
- **Priority matrix**: P0-P3 with expected impact

Output template:

```
## 一、脚本概况
## 二、致命Bug
## 三、重要逻辑缺陷
## 四、模型架构优化建议
## 五、训练策略优化建议
## 六、优先级排序
## 七、总结
```

### Phase 3: Save to Vault with Cross-links

1. **Add YAML frontmatter** with tags, created date, source path
2. **Place in correct directory**: `projects/` for bidding/analysis, `振动信号处理/` for domain knowledge
3. **Cross-link to related notes**: search for existing notes on related topics, add bidirectional links
4. **Index to vector memory**: `memory_vec(action='add', content='concise 1-3 sentence summary', tags=[...])`

### Phase 4: Verify Cross-links

After saving, verify:
- The new note has a `关联笔记` section listing all related notes
- At least the most comprehensive related note has a backlink to the new note
- Vector memory entry exists for semantic recall

## Key Pitfalls

- **Do NOT** leave `.docx`/`.pdf` in the vault — convert to `.md` first
- **PDF is binary** — `read_file` alone cannot extract text; use pymupdf
- **Risk assessment is not optional** — every project analysis must include a risk section
- **Cross-links must be bidirectional** — a note without `[[wikilinks]]` is an orphan
- **Vector memory should be concise** (1-3 sentences), not a full-text dump
- **Always check `session_search` first** for prior analysis of the same document