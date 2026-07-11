---
name: bidding-requirements-analysis
description: >
  招标技术需求书分析与技术门槛补充。阅读投标/招标技术需求文档（.docx），识别其中
  对投标人资质和能力的薄弱环节，补充硬性技术门槛以有效筛选竞争对手。
  TRIGGER: "分析招标技术需求书", "补充技术门槛", "提高投标门槛",
  "分析这个招标文件", "看下这个标书有什么漏洞", "补充技术壁垒"
  SKIP: 纯商务/财务类标书分析，不涉及技术需求的部分
---

# 招标技术需求书分析与技术门槛补充

## 核心原则

招标技术需求书的"技术门槛"不是越严越好，而是要**精准卡位**——卡在竞争对手最薄弱的环节上，同时不影响自己团队的能力范围。

## 标准工作流

### 1. 读取文档

```python
from docx import Document
doc = Document("/path/to/标书.docx")
```

完整读取所有段落，理解文档结构：总则、分模块技术要求、交付物、验收标准、投标人技术方案要求。

### 2. 识别薄弱环节

从以下维度审计原始文档：

| 审计维度 | 检查要点 | 常见问题 |
|---------|---------|---------|
| **投标人资质** | 是否有团队经验、项目案例、认证要求？ | 大多标书没有资质要求，通用软件团队也能投 |
| **算法精度标准** | 对标哪个行业标准？偏差容忍度多少？ | 很多标书不提对标，或偏差太宽松 |
| **性能指标** | 是否有量化性能指标？ | 常缺失实时性、并发性、大文件处理等指标 |
| **硬件适配** | 是否要求国产化适配？ | 不要求国产 GPU = 国外团队也能投 |
| **验收标准** | 验收方式是否严格？ | 无第三方验收、无代码质量审查 |
| **数据安全** | 加密、合规、容灾要求？ | 常缺失或过于笼统 |

### 3. 设计技术门槛

**最高效的 7 类门槛**（按杀伤力排序）：

| 门槛类型 | 杀伤力 | 设计要点 |
|---------|--------|---------|
| **算法精度对标** | ⭐⭐⭐⭐⭐ | 要求投标阶段即提交与行业标杆软件（如 B&K PULSE、Siemens LMS、Head Acoustics）的对标测试数据。没做过声学工程化的团队根本交不出来 |
| **国产硬件适配** | ⭐⭐⭐⭐⭐ | 要求同时支持 NVIDIA + 国产 GPU（昇腾/寒武纪/海光至少一种），投标时提交国产 GPU 性能测试报告 |
| **现场代码复现** | ⭐⭐⭐⭐ | 验收时从零手写核心算法（如心理声学指标、滤波算法），与已交付模块计算结果比对 |
| **核心团队经验** | ⭐⭐⭐⭐ | 要求核心成员 3 年+ 行业经验，提供简历/合同证明，验收时到岗不得更换 |
| **行业案例数量** | ⭐⭐⭐⭐ | 要求近 3 年 N 个同类项目，金额下限，包含特定格式经验 |
| **第三方验收** | ⭐⭐⭐ | 由 CMA/CNAS 资质机构验收，费用由投标人承担 |
| **数据安全合规** | ⭐⭐⭐ | 等保三级、AES-256 加密、两地三中心容灾 |

### 4. 格式化为标书条款

每个门槛写成标准投标条款格式：
- 以"（N）"开头编号
- 包含可量化、可验证的硬性指标（数字、百分比、时限）
- 写明验收方式和不合格后果

### 5. 合成到原始文档

使用 python-docx 将新条款插入标书对应章节：

```python
from docx import Document
from docx.shared import Pt, RGBColor

doc = Document("/path/to/原始标书.docx")

def find_anchor(doc, text_keyword):
    for p in doc.paragraphs:
        if text_keyword in p.text:
            return p
    return None

def add_para_after(doc, anchor, text, bold=False, font_size=None, color_rgb=None):
    new_p = doc.add_paragraph(text)
    anchor._element.addnext(new_p._element)
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

def add_section(doc, anchor_text, heading_text, body_lines):
    anchor = find_anchor(doc, anchor_text)
    if not anchor:
        return False
    current = anchor
    current = add_para_after(doc, current, heading_text,
                              bold=True, font_size=12,
                              color_rgb=RGBColor(0x1A, 0x3C, 0x6E))
    for line in body_lines:
        current = add_para_after(doc, current, line)
    return True
```

## 常见插入位置与锚点

| 新条款 | 插入位置（锚点文本） | 目标章节 |
|--------|-------------------|---------|
| 投标人资质经验要求 | "1.3 通用约束要求" 或类似 | 第一章总则末尾 |
| 算法精度对标 | "2.4.8 配套功能" 或类似 | 信号分析模块末尾 |
| 格式兼容性深度验证 | "ATFX 文件上传、读取、解析" 或类似 | 数据格式章节 |
| 本地大模型硬件适配 | "2.5.4 迭代拓展能力" 或类似 | 大模型章节末尾 |
| 验收测试专项要求 | "（6）配套工具：" 或类似 | 交付物章节末尾 |
| 实时流式/高并发 | "（5）功能验收：所有声学" 或类似 | 性能验收章节 |
| 数据安全合规 | "（7）系统安全保障方案" 或类似 | 投标方案要求末尾 |

## 避免的陷阱

- **不要写无法验证的定性要求**："技术方案先进" → 必须换成"偏差 ≤ 0.5 dB"这种可量化指标
- **不要只限制一个品牌**：要求"B&K 对标"而非"B&K 软件"——单品牌限制容易被质疑招标歧视
- **注意条款之间的逻辑一致性**：2.4.9 要求对标，5.2 验收标准中要有对应验收条款
- **保留自留空间**：确保自己团队（或意向合作方）具备满足这些门槛的能力，避免搬石头砸自己脚
- **投标阶段要求附件**：把最硬的门槛（如对标数据、案例证明）放在投标阶段要求提交，这样投标截止前就能筛掉不具备实力的投标人

## 参考文件

- `references/technical-barrier-templates.md` — 各类技术门槛的标准化条款模板（中文）
- `references/section-insertion-examples.md` — 实际标书条款插入案例（来自本会话实践）