---
name: docx-author
description: Read, edit, and generate .docx files headless with python-docx — paragraph insertion at anchors, text replacement, basic formatting, batch operations. Use for bidding documents, contracts, reports, and any structured Word document automation.
version: 1.0.0
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docx, word, document, python-docx, office]
    related_skills: [excel-author, pptx-author]
---

# docx-author

Programmatic `.docx` manipulation using `python-docx`. Covers reading, targeted paragraph insertion, text search/replace, formatting, and batch operations.

## Setup

```bash
pip install python-docx
```

## Core patterns

### Reading a .docx

```python
from docx import Document
doc = Document("input.docx")
for i, p in enumerate(doc.paragraphs):
    print(f"[{i}] {p.text[:100]}")
```

`doc.paragraphs` is a flat list of all paragraph objects. Each has `.text` for content and `.runs` for formatted sub-strings.

### Finding a paragraph by text anchor

```python
def find_paragraph(doc, text_keyword):
    for i, para in enumerate(doc.paragraphs):
        if text_keyword in para.text:
            return para, i
    return None, -1
```

**Always use partial match (`in`) not exact match** — docx paragraphs may contain extra whitespace, hidden characters, or field codes.

### Inserting a paragraph AFTER a specific paragraph

This is the most common editing operation — and python-docx has **no built-in `.insert_paragraph_after()`**. Use XML manipulation:

```python
from docx.shared import Pt, RGBColor

def add_para_after(doc, anchor_para, text, bold=False, font_size=None, color_rgb=None):
    """Add a new paragraph right after anchor_para using XML node manipulation."""
    new_p = doc.add_paragraph(text)
    anchor_para._element.addnext(new_p._element)  # KEY: moves <w:p> after anchor
    if bold and new_p.runs:
        for run in new_p.runs:
            run.bold = True
    if font_size and new_p.runs:
        for run in new_p.runs:
            run.font.size = Pt(font_size)
    if color_rgb and new_p.runs:
        for run in new_p.runs:
            run.font.color.rgb = color_rgb
    return new_p
```

**Key insight**: `doc.add_paragraph()` appends to the end of the document's XML tree. `anchor_para._element.addnext(new_p._element)` surgically moves it right after the anchor in the XML sibling order. The paragraph IS in the document from that point — no need to call `.save()` before reading it back.

### Inserting a multi-paragraph section

```python
def add_section(doc, anchor_text, heading_text, body_lines):
    """Insert a heading + body lines after the paragraph containing anchor_text."""
    anchor = find_paragraph(doc, anchor_text)[0]
    if not anchor:
        print(f"  [WARN] Anchor '{anchor_text}' not found!")
        return False
    
    current = anchor
    current = add_para_after(doc, current, heading_text, bold=True, font_size=12,
                              color_rgb=RGBColor(0x1A, 0x3C, 0x6E))
    for line in body_lines:
        if line.strip():
            current = add_para_after(doc, current, line)
        else:
            current = add_para_after(doc, current, "")
    return True
```

### Inserting a paragraph BEFORE a specific paragraph

```python
def add_para_before(doc, anchor_para, text):
    new_p = doc.add_paragraph(text)
    anchor_para._element.addprevious(new_p._element)
    return new_p
```

### Finding text with partial match

When the exact text isn't known, try progressively shorter anchor strings:

```python
# First try the exact string
for candidate in [full_string, partial_string, short_keyword]:
    anchor = find_paragraph(doc, candidate)[0]
    if anchor:
        break
```

## Text formatting

### Bold a paragraph

```python
p = doc.add_paragraph("Important text")
for run in p.runs:
    run.bold = True
```

### Mixed formatting (bold within normal text)

```python
p = doc.add_paragraph()
p.add_run("Normal text ")
run = p.add_run("BOLD text")
run.bold = True
p.add_run(" normal again")
```

### Font size, color, and name

```python
from docx.shared import Pt, RGBColor
run = p.add_run("Styled text")
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)  # dark blue
run.font.name = "宋体"
```

Use `RGBColor(0x1A, 0x3C, 0x6E)` for section heading colors — looks professional in Chinese bidding documents.

### Font for Chinese text

```python
from docx.oxml.ns import qn
run.font.name = 'Times New Roman'  # western font
r = run._element
r.rPr.rFonts.set(qn('w:eastAsia'), '黑体')  # CJK font
```

## Text search and replace

python-docx has no built-in find-and-replace. For simple cases:

```python
def replace_text(doc, old_text, new_text):
    for p in doc.paragraphs:
        if old_text in p.text:
            # Clear and rebuild
            inline = p.runs
            for i in range(len(inline)):
                if old_text in inline[i].text:
                    inline[i].text = inline[i].text.replace(old_text, new_text)
```

For complex cases (text split across runs), use a helper that concatenates all runs, replaces, and redistributes.

## Common workflows

### Workflow 1: Insert supplementary clauses into a bidding document

```python
doc = Document("技术需求v6.docx")
add_section(doc, "1.3 通用约束要求", "1.4 投标人必备资质与经验要求", [
    "（1）核心团队经验要求：...",
    "（2）同类项目案例要求：...",
])
doc.save("技术需求v6_补充版.docx")
```

### Workflow 2: Replace a specific table cell

```python
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if "old value" in cell.text:
                cell.text = "new value"
```

### Workflow 3: Merge two documents

```python
from docx import Document as Doc

main = Doc("main.docx")
insert = Doc("insert.docx")

# Copy all paragraphs from insert to main
for para in insert.paragraphs:
    # Clone paragraph XML element
    main.element.append(para._element)
```

### Workflow 4: Create a Chinese budget/bid quotation table from scratch

Building a complete budget table (模块-子项-分项预算-模块合计-总合计) with proper Chinese formatting, styling, and constraint checking:

```python
modules = [
    {
        'name': '模块一：数据库模块',
        'items': [
            ('工作项描述', 14),   # 14 = ¥14,000
        ],
        'subtotal': 68,
    },
]
total = sum(m['subtotal'] for m in modules) * 1000  # 500,000
```

See `references/chinese-budget-table.md` for full implementation: table setup, cell shading helpers, font configuration, money formatting, and constraint checking.

For **full quotation document generation** (cover page, categorized hardware tables, software breakdown, consolidated summary, commercial terms), see `references/quotation-document-structure.md`.

## Pitfalls

1. **`insert_paragraph_after()` does NOT exist** in python-docx. Always use the `_element.addnext()` trick.
2. **`addnext()` acts on XML siblings**, not tree depth. It inserts at the same level as the anchor element.
3. **Paragraphs are not re-indexed** after insertion. `doc.paragraphs` returns a fresh list each access.
4. **Multi-run text**: `p.text` concatenates all runs. `p.runs` gives access to individual formatted segments. When matching, use `p.text`; when formatting, use `p.runs`.
5. **Table paragraphs** are children of table cells, not direct children of the document body. Use `doc.tables[0].rows[0].cells[0].paragraphs` to access them.
6. **`doc.save()` overwrites silently** — keep backups when editing critical documents.
7. **Blank paragraphs** created via `add_paragraph("")` still produce empty `<w:p>` XML elements. They show as blank lines.
8. **Font color on new paragraphs**: the first `add_run()` creates the initial run automatically; subsequent formatting needs explicit `run.font.color.rgb = ...`.
9. **Multiple saves**: each `doc.save()` writes the full document. No need to save between insertions — save once at the end.
10. **Large documents** (>500 paragraphs) can be slow. Batch all edits before saving once.

## When NOT to use this skill

- User has a live Word instance — use Office COM/MCP instead
- Pure data export (CSV/JSON) — use simpler formats
- Chart-heavy documents with complex formatting — use `pptx-author` or LaTeX