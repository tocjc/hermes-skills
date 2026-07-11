# 标书条款插入案例 — 车辆噪声测试与分析后端软件

## 原始文档结构

来源：`车辆噪声测试与分析后端软件及算法开发招标技术需求书`（v6 版）

六大模块：数据库、声纹知识库、大数据训练、噪声信号基础分析、本地大语言模型、配套工具

## 成功插入的 7 个条款

### 1.4 投标人必备资质与经验要求
**插入位置**：第一章"项目总则"末尾，1.3 通用约束要求之后
**锚点文本**：`1.3 通用约束要求`
**核心内容**：6 条要求 — 团队经验、案例、声学工程化、大模型部署、ISO 9001/CMMI、知识产权

### 2.4.9 算法精度对标与验证要求
**插入位置**：2.4 节末尾，2.4.8 配套功能之后
**锚点文本**：`2.4.8 配套功能`
**核心内容**：对标 B&K PULSE / LMS Test.Lab / Head Acoustics Artemis，偏差≤0.5dB/3%/5%，投标阶段提交对标数据

### 2.5.5 本地大模型硬件适配与性能要求
**插入位置**：2.5 节末尾，2.5.4 迭代拓展能力之后
**锚点文本**：`2.5.4迭代拓展能力`
**核心内容**：NVIDIA + 国产 GPU 双适配，INT4/INT8 量化精度下降≤2%，10,000 条 NVH 微调数据集

### 3.1.4 ATFX 文件格式兼容性深度验证
**插入位置**：3.1 节末尾
**锚点文本**：`ATFX 文件上传、读取、解析、批量转换接口需单独开发`
**核心内容**：多厂商兼容矩阵、元数据结构深度解析、文件完整性校验、≥2GB 超大文件处理

### 4.7 验收测试专项要求
**插入位置**：第四章"交付物要求"末尾
**锚点文本**：`（6）配套工具：`
**核心内容**：第三方 CMA/CNAS 验收、SonarQube 代码质量扫描、现场重写算法验证、3 年运维

### 5.6 实时流式处理能力要求 + 5.7 高并发处理能力要求
**插入位置**：第五章"性能与验收标准"末尾
**第一个锚点**：`（5）功能验收：所有声学`
**第二个锚点**：`（4）历史数据回放分析`（自动关联前一个插入项）
**核心内容**：WebSocket/gRPC 实时流式、≤500ms 延迟、50 路并发、GPU 调度

### 6.8 数据安全与合规专项要求
**插入位置**：第六章"投标人技术方案要求"末尾
**锚点文本**：`（7）系统安全保障方案`
**核心内容**：AES-256 加密、TLS 1.3、数据脱敏、等保三级、两地三中心容灾

## 插入实现代码

```python
from docx import Document
from docx.shared import Pt, RGBColor

doc = Document("/path/to/标书.docx")

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

## 关键技巧

1. **锚点文本选择**：优先选择段落中唯一的、不与其他段落重复的字符串。如果第一次锚点没找到，改用更长的文本片段（如完整句子）重试
2. **连续插入**：在同一章节插入多个子条款时，后一个条款的锚点选择前一个条款末尾的句子，确保插入顺序正确
3. **标题样式**：新插入的章节标题用 bold=True + 12pt + 深蓝色 (#1A3C6E)，与原始文档标题风格一致
4. **保存前验证**：用 `len(doc.paragraphs)` 检查段落数是否增加，用 `find_anchor()` 验证新插入的标题文本存在