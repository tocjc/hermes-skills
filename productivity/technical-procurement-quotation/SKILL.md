---
name: technical-procurement-quotation
description: "Generate detailed procurement quotations from technical specification PDFs. Pipeline: read/analyze PDF → extract hardware/software requirements → research market products with pricing → build structured quotation → output as Word document. Use when user asks to 'read a technical spec and make a quotation', 'list equipment needed and price', 'create a procurement quote from this PDF', '逐项列出一台设备所需硬件并报价'."
version: 1.0.0
author: Agent
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [quotation, procurement, technical-spec, bidding, word-document, pricing]
    related_skills: [docx-author, bidding-requirements-analysis, technical-requirements-analysis]
---

# Technical Procurement Quotation

Generate detailed procurement quotations from technical specification PDFs. This skill covers the full pipeline: reading and analyzing technical documents, extracting hardware and software requirements, researching market-available products with pricing, building a structured quotation with proper breakdowns, and outputting as a professional Word document.

## When to use

User says things like:
- "阅读分析这份技术文件，逐项列出一台设备配套所需采购的硬件设备"
- "按照技术文件要求，推荐满足要求的市场主流产品，做出一份详细报价"
- "分析技术文件中系统集成的需要，做一份软件开发的报价"
- "合并硬件报价、软件报价，给出一份详细完整的系统报价，输出采用Word格式文件"
- "这是技术规格书，帮我做一份采购报价"

## Workflow

### Phase 1: Read and analyze the technical specification

```bash
python3 -c "
import pymupdf
doc = pymupdf.open('/path/to/document.pdf')
for i, page in enumerate(doc):
    text = page.get_text()
    if text.strip():
        print(f'===== PAGE {i+1} =====')
        print(text)
"
```

Key extraction targets:
- **System architecture** — diagram description, components, data flow
- **Hardware requirements** — sensors, data acquisition units, PLCs, switches, servers, cabling, enclosures
- **Software requirements** — data interfaces, management tools, protocol integration, deployment
- **Specification tables** — sensor parameters, channel counts, environmental ratings, certifications
- **Configuration lists** — recommended BOMs, parts lists with quantities
- **Acceptance criteria** — testing, quality assurance, documentation
- **Commercial terms** — warranty, delivery, payment milestones

### Phase 2: Extract hardware requirements

For each hardware category, capture:

| Category | What to extract |
|----------|----------------|
| **Sensors** | Type, sensitivity, range, frequency response, IP rating, temp range, quantity, mounting method |
| **Data Acquisition** | Channel count, ADC bits, sample rate, storage, interfaces, edge computing, enclosure size |
| **PLC/Controllers** | Model, I/O modules, communication buses, power supply |
| **Computers/Servers** | CPU, RAM, storage, operating temperature, form factor |
| **Network** | Switch type (ports/fiber), router, cable types, lengths |
| **Cabling & Accessories** | Cable specs, connectors, mounts, brackets, adhesives, labels |
| **Enclosures/Cabinets** | Dimensions, material, mounting |

### Phase 3: Research market products

For each hardware item, determine:
- **Recommended brand/model** — market-leading, technically compliant
- **Product specifications** — must meet or exceed the technical spec
- **Market price** — reasonable unit price based on industry knowledge
- **Quantity** — per the technical spec's configuration list

When in doubt about pricing, use reasonable market estimates and note them as estimates. Common sources:
- Industrial sensor pricing: PCB Piezotronics, B&K, 东华测试
- PLC pricing: Beckhoff, Siemens, Schneider
- Industrial PC pricing: Advantech (UNO/ARK series)
- Network equipment: 华为, 光谱森科, 烽火通信

### Phase 4: Build the quotation structure

Organize the quotation into clear sections:

```
1. Hardware per unit (single turbine/machine)
   1.1 Sensors
   1.2 Data Acquisition Unit (CMS)
   1.3 PLC-CMS Integrated Controller
   1.4 Communication & Network Equipment
   1.5 Industrial PC/Server
   1.6 Installation Accessories & Cables
   1.7 Cabinets/Enclosures
   → Hardware subtotal per unit

2. Shared equipment (for whole site/project)
   → Data server, firewall, isolation devices

3. Software development (system integration, NOT fault diagnosis algorithms)
   3.1 Data Interface Service
   3.2 Lower-level Management Software
   3.3 Data Collection & Storage Management
   3.4 Communication Protocol Integration
   3.5 System Deployment & Commissioning
   → Software subtotal

4. Comprehensive quotation summary
   → Hardware + Software + Shared equipment = Total
```

### Phase 5: Generate Word document

Use `docx-author` skill for Word generation. The document should include:

**Cover page:**
- Project name
- Document version
- Date
- Preparing organization

**Table of contents**

**Sections:**

1. **Project Overview** — brief description of the system
2. **Hardware Configuration & Pricing** — per-category tables with:
   - Item name, specification/model, recommended brand, quantity, unit price
   - Subtotal per category
   - Single-unit hardware total
3. **Shared Equipment** — server, firewall, isolation devices
4. **Software Development Quotation** — per-module breakdown:
   - Work item, description, effort (person-days), amount
   - Software subtotal
5. **Comprehensive Quotation Summary** — consolidated table
6. **Commercial Terms** — payment milestones, delivery, warranty, training

**Table formatting:**
```python
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT

table = doc.add_table(rows=N, cols=5)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
# Header row: bold, 9pt
for i, h in enumerate(headers):
    table.rows[0].cells[i].text = h
    for p in table.rows[0].cells[i].paragraphs:
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(9)
# Data rows: 9pt
for i, row_data in enumerate(data):
    for j, val in enumerate(row_data):
        table.rows[i+1].cells[j].text = val
        for p in table.rows[i+1].cells[j].paragraphs:
            for r in p.runs:
                r.font.size = Pt(9)
# Total row: bold, colored
grand_total = doc.add_paragraph()
grand_total.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = grand_total.add_run('总报价：¥XXX,XXX')
run.font.bold = True
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(204, 0, 0)
```

**Chinese font setup:**
```python
from docx.oxml.ns import qn
style = doc.styles['Normal']
font = style.font
font.name = 'SimSun'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
```

### Phase 6: Save analysis to knowledge base

After generating the Word document, also save a structured Markdown summary to the Obsidian vault:

```markdown
---
tags: [project-specific tags]
created: YYYY-MM-DD
---

# Project Name — Quotation Analysis

## System Architecture
...

## Hardware Configuration (per unit)
| Category | Item | Qty |
|----------|------|:---:|
| ... | ... | ... |

## Quotation Summary
| Item | Amount |
|------|------:|
| Hardware per unit | XXX |
| Shared equipment | XXX |
| Software | XXX |
| **Total** | **XXX** |
```

## Key pitfalls

1. **PDF text extraction**: Use pymupdf (fitz). Raw PDF binary can't be read directly — always extract text with `page.get_text()`.
2. **pymupdf installation**: `pip install pymupdf`. If not available, install first.
3. **python-docx installation**: `pip install python-docx`. Required for Word output.
4. **Market pricing**: When exact prices are unknown, use reasonable estimates and clearly note they are estimates. Provide a range rather than a single number when uncertain.
5. **Software vs hardware separation**: The user often asks to separate "system integration software" from "fault diagnosis algorithm" development. Keep these distinct.
6. **Knowledge base archiving**: Always save the analysis to the Obsidian vault under `projects/` after generating the Word document. The user will ask "where is the report saved?"
7. **Chinese formatting**: For Word documents, always set proper Chinese fonts (SimSun for body, SimHei or similar for titles) using the `qn('w:eastAsia')` method.
8. **N-tier pricing**: The quotation may need to support N units (e.g., N=1 for demo, actual N from the project). Always provide both per-unit pricing and the formula for N units.

## References

- [[docx-author]] — Word document generation with python-docx
- [[technical-requirements-analysis]] — technical requirements analysis patterns
- `docx-author/references/chinese-budget-table.md` — Chinese budget table formatting