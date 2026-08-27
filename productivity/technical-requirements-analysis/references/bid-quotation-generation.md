# 投标报价书生成指南

从技术需求分析到 Word 投标报价书的完整工作流。

## 触发场景

完成技术需求分析并交付解决方案后，用户要求"做一份投标报价"、"做预算"、"出报价书"时使用。

## 前置条件

已有技术需求分析的逐条解决方案（由 `technical-requirements-analysis` 技能产出），包含：
- 按模块分类的需求-方案对照表
- 开源软件选型与授权分析
- 项目难点评估
- 开发周期规划（含人力估算）

## 工作流

### Step 1: 拆解模块 → 成本项

将方案中的每个模块进一步拆分为可直接定价的工作项：

| 费用类型 | 包含内容 | 单价参考 |
|---------|---------|---------|
| 人工费 | 人天 × 单价（通常 0.8-1.2 千元/人天） | 按模块工作量估算 |
| 软件许可/第三方组件 | 开源组件集成、商业化授权 | 按实际选型 |
| 其他费用 | GPU算力消耗、硬件校准、测试资源 | 按项报价 |

### Step 2: 汇总约束

- **总预算上限**（如 ¥500,000）
- **最小计价单位**（通常 1 千元 = ¥1,000）
- **预备金**（不可预见费，通常占总价 5%）
- **各项金额取整到最小单位**

### Step 3: 构建报价表

每个模块一张数据行表，核心辅助函数：

```python
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from lxml import etree

def set_shading(cell, color):
    cell._tc.get_or_add_tcPr().append(
        parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>'))

def cell_text(cell, text, bold=False, size=10, align=WD_ALIGN_PARAGRAPH.LEFT, color=None):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    r = p.add_run(str(text))
    r.font.size = Pt(size)
    r.font.name = 'Times New Roman'
    rPr = r._element.get_or_add_rPr()
    rPr_fonts = rPr.find(qn('w:rFonts'))
    if rPr_fonts is None:
        rPr_fonts = etree.SubElement(rPr, qn('w:rFonts'))
    rPr_fonts.set(qn('w:eastAsia'), '宋体')
    r.bold = bold
    if color:
        r.font.color.rgb = color
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    return r

def make_table(headers, rows):
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = 'Table Grid'
    for j, h in enumerate(headers):
        cell_text(t.rows[0].cells[j], h, bold=True, size=9,
                  align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(255, 255, 255))
        set_shading(t.rows[0].cells[j], '1A3C6E')
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            text = str(val).replace('**', '')
            bold = isinstance(val, str) and val.startswith('**')
            align = WD_ALIGN_PARAGRAPH.CENTER if j in (0, 2, 3, 4, 5) else WD_ALIGN_PARAGRAPH.LEFT
            cell_text(t.rows[i + 1].cells[j], text, bold=bold, size=9, align=align)
        if any('小计' in str(v) for v in row):
            for j in range(len(headers)):
                set_shading(t.rows[i + 1].cells[j], 'E8EDF5')
    return t
```

### Step 4: 文档结构

```
封面 → 项目概述 → 报价汇总表 → 分项明细（每模块一张表） → 商务条款
```

**商务条款必含**：付款方式（4:3:3:1）、开发周期里程碑、交付物清单、售后服务、报价说明（不包含项、有效期、含税说明）。

### Step 5: 金额核实

写入前核实：
- 各模块小计之和 + 预备金 = 总报价
- 每项金额 ≥ 最小单位（1 千元）
- 总报价 ≤ 预算上限

## Pitfalls

### ❌ 新建 run 的 rPr 为 None

```python
# 崩溃：
r.font.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 正确：
rPr = r._element.get_or_add_rPr()
rPr_fonts = rPr.find(qn('w:rFonts'))
if rPr_fonts is None:
    rPr_fonts = etree.SubElement(rPr, qn('w:rFonts'))
rPr_fonts.set(qn('w:eastAsia'), '宋体')
```

### ❌ 单脚本过长导致超时

将 Python 脚本写为 `.py` 文件保存到 `/tmp/`，通过 `terminal(command="python3 /tmp/gen.py")` 执行，而非用 `execute_code`。

### ❌ 忘记预备金

总报价 = 模块小计之和 + 预备金（5%），否则成本覆盖不足。