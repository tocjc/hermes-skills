# Chinese Budget / Bid Quotation Table Pattern (python-docx)

Building a structured budget table from scratch in python-docx — used for 投标报价书、项目预算表、报价明细表.

## Key Pattern: Module → Items → Subtotal → Grand Total

Structure every budget table the same way:

```
┌──────┬──────────────────────────┬────────────┬────────────┐
│ 序号 │ 模块名称 / 细分工作项     │ 分项预算(元)│ 模块合计(元)│
├──────┼──────────────────────────┼────────────┼────────────┤
│      │ 模块一：XXX              │            │  ¥68,000   │ ← bold, colored
├──────┼──────────────────────────┼────────────┼────────────┤
│  1   │   具体工作项描述          │  ¥14,000   │            │
│  2   │   具体工作项描述          │  ¥12,000   │            │
├──────┼──────────────────────────┼────────────┼────────────┤
│      │ 模块二：XXX              │            │  ¥57,000   │
├──────┼──────────────────────────┼────────────┼────────────┤
│  ... │                          │            │            │
├──────┼──────────────────────────┼────────────┼────────────┤
│      │ 项 目 总 合 计            │            │ ¥500,000   │ ← bold, red, orange bg
└──────┴──────────────────────────┴────────────┴────────────┘
```

## Data Structure

```python
modules = [
    {
        'name': '模块一：数据库模块',
        'items': [
            ('工作项描述1', 14),    # 14 = 14,000元
            ('工作项描述2', 12),
        ],
        'subtotal': 68,           # sum of items in 千元
    },
]
total = sum(m['subtotal'] for m in modules) * 1000
```

All item prices are stored in **千元 (thousands)** — multiply by 1000 only at display time. This keeps totals clean and makes constraint checking trivial.

## Table Setup

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

doc = Document()
table = doc.add_table(rows=1, cols=4)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'

# Column widths (adjust per content)
for row in table.rows:
    row.cells[0].width = Cm(0.8)   # 序号
    row.cells[1].width = Cm(8.7)   # 模块/工作项
    row.cells[2].width = Cm(2.5)   # 分项预算
    row.cells[3].width = Cm(2.5)   # 模块合计
```

## Cell Styling Helpers

### Header row (dark blue background, white text)

```python
def add_heading_row(table, row_idx, texts, bg_color='1A3C6E'):
    row = table.rows[row_idx]
    for i, text in enumerate(texts):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        set_cell_shading(cell, bg_color)
```

### Data row (left-aligned item name, center-aligned amounts)

```python
def add_data_row(table, row_idx, texts, last_col_bold=False, last_col_color=None, bg_color=None):
    row = table.rows[row_idx]
    for i, text in enumerate(texts):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(str(text))
        run.font.size = Pt(10)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        if last_col_bold and i == len(texts) - 1:
            run.bold = True
        if last_col_color and i == len(texts) - 1:
            run.font.color.rgb = last_col_color
        if bg_color:
            set_cell_shading(cell, bg_color)
```

### Cell shading

```python
def set_cell_shading(cell, color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)
```

## Common Colors for Chinese Financial Docs

| Use | Hex |
|-----|-----|
| Header bg | `1A3C6E` (dark navy) |
| Module-title row bg | `E8F0FE` (light blue) |
| Grand-total row bg | `FFF3E0` (light orange) |
| Grand-total text | `CC0000` (red) |
| Module-subtotal text | `1A3C6E` (dark navy) |
| Section heading text | `1A3C6E` (dark navy) |
| Note/annotation text | `666666` (grey) |

## Font Setup for Chinese Text

Every run that contains Chinese characters needs both the western and CJK font:

```python
from docx.oxml.ns import qn

def set_run_font(run, western='宋体', cjk='宋体', size=Pt(10)):
    run.font.name = western
    run.font.size = size
    run._element.rPr.rFonts.set(qn('w:eastAsia'), cjk)
```

## Money Formatting

```python
# Store in 千元, display as 元
price_display = f'¥{price_in_qian * 1000:,}'

# Module subtotal
subtotal_display = f'¥{mod["subtotal"] * 1000:,}'

# Grand total
total_display = f'¥{total * 1000:,}'
```

## Document-Level Styling

```python
# Global font
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# Page margins
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
```

## Constraint Checking Pattern

Before final output, verify:

```python
assert total <= 500, f"Total {total}K exceeds 500K limit"
for mod in modules:
    calculated = sum(item[1] for item in mod['items'])
    assert calculated == mod['subtotal'], \
        f"{mod['name']}: items sum {calculated} != declared subtotal {mod['subtotal']}"
    for item in mod['items']:
        assert item[1] % 1 == 0, f"Item {item[0]}: not in 1K increments"
```

## Full Example Output

```
车 辆 噪 声 测 试 与 分 析 后 端 软 件 及 算 法 开 发 项 目
项 目 投 标 报 价 书
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

项目名称    车辆噪声测试与分析后端软件及算法开发项目
技术方案    基于《XX解决方案》
预算总额    ¥500,000.00（人民币伍拾万元整）
报价单位    （单位名称）

预算编制说明：...总预算控制在...以内，分项预算最小单位为壹仟元...

| 序号 | 模块/工作项                          | 分项预算   | 模块合计   |
|------|--------------------------------------|------------|------------|
|      | 模块一：数据库模块                    |            | ¥68,000    |
|  1   |   高性能业务数据库+MinIO架构搭建      | ¥14,000    |            |
| ...  |                                      |            |            |
|      | 项 目 总 合 计                       |            | ¥500,000   |

备注：
1. 本报价基于全部开源技术栈构建...
2. 报价不含硬件设备...
3. 分项预算最小单位为壹仟元...
4. 报价有效期：自报价之日起90个自然日。
```