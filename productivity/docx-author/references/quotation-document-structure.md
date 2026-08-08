# Quotation Document Structure (Technical Procurement)

Full document structure for generating a technical procurement quotation Word document from a hardware specification PDF.

## Document layout

### Cover page
```python
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# Chinese font setup
style = doc.styles['Normal']
font = style.font
font.name = 'SimSun'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

# Title
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('Project Name\nQuotation')
run.font.size = Pt(26)
run.font.bold = True
run.font.color.rgb = RGBColor(0, 51, 102)

# Info table
info_items = [('Project No', 'XXX'), ('Date', '2026-XX-XX'), ('Company', 'XXX')]
table = doc.add_table(rows=len(info_items), cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, (k, v) in enumerate(info_items):
    table.rows[i].cells[0].text = k
    table.rows[i].cells[1].text = v
```

### Table of contents
Use `doc.add_heading('目  录', level=1)` followed by a list of sections.

### Hardware section
Per-category tables with this format:

```python
table = doc.add_table(rows=N, cols=6)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
```

Headers: `['序号', '产品名称', '规格型号', '推荐品牌', '数量', '单价(元)']`

### Subtotal paragraph
```python
subtotal = doc.add_paragraph()
run = subtotal.add_run('Category subtotal: ¥XXX,XXX')
run.font.bold = True
run.font.size = Pt(11)
```

### Software section
Headers: `['序号', '工作项', '说明', '工作量（人天）', '金额（元）']`

### Summary table
```python
final_table = doc.add_table(rows=8, cols=3)
final_table.style = 'Light Grid Accent 1'
```

Rows: hardware, shared equipment, software, hardware subtotal, software subtotal, installation, TOTAL.

### Grand total
```python
grand_total = doc.add_paragraph()
grand_total.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = grand_total.add_run('总报价：¥XXX,XXX（人民币大写）')
run.font.bold = True
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(204, 0, 0)
```

## Notes section
Use `doc.add_paragraph('Note text', style='List Bullet')` for numbered notes.

## Page breaks
```python
doc.add_page_break()
```