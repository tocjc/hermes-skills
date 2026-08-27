---
name: domain-modeling
description: 领域建模 — 构建/打磨 CONTEXT.md 共享语言和 ADR 决策记录。
---

# Domain Modeling Skill — 领域建模

源自 Matt Pocock 的 `domain-modeling` 技能。核心：**主动构建和打磨项目的领域模型** — 挑战术语、编制场景、实时更新 CONTEXT.md 和 ADR。

## 触发场景

- 讨论代码库术语或领域概念时
- 编写或修改 `CONTEXT.md` / `AGENTS.md` 时
- 记录或编辑 ADR（架构决策记录）时
- 团队讨论中有人用词不精确，需要统一术语时
- 项目开始时需要建立共享语言时

## 文件结构

### 单上下文（大多数项目）

```
/
├── CONTEXT.md           ← 共享术语表，无实现细节
├── docs/
│   └── adr/             ← 架构决策记录
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

### 多上下文

如果根目录存在 `CONTEXT-MAP.md`，则项目有多个上下文：

```
/
├── CONTEXT-MAP.md       ← 指向各上下文
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

按需创建文件 — 有内容才创建。

## CONTEXT.md 格式

```
# {上下文名称}

{一两句描述，说明这个上下文是什么}

## Language

**Order**:
{一两句术语定义}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request
```

### 规则

- **要有观点** — 同一个概念有多个词，选最好的，其他列在 `_Avoid_`
- **定义要紧凑** — 一两句，定义 WHAT 不是 WHAT IT DOES
- **只包含领域特有术语** — 通用编程概念（timeout, error type, utility）不放进 CONTEXT.md
- **自然分组** — 相关术语归到子标题下

## 工作流程

### 1. 挑战术语

当用户使用的词与 CONTEXT.md 中的现有术语冲突时，立即指出：
> "你的词汇表里定义 'cancellation' 是 X，但你似乎在说 Y — 是哪个？"

### 2. 打磨模糊语言

当用户使用模糊或过载的术语时，提出精确的规范术语：
> "你说 'account' — 是指 Customer 还是 User？这是两个不同的东西。"

### 3. 讨论具体场景

当领域关系在讨论时，用具体场景做压力测试：
> "如果用户下了订单后又修改了地址，Order 的状态是什么？"

### 4. 交叉验证代码

当用户说某个东西如何工作时，检查代码是否一致：
> "你的代码 cancel 整个 Order，但你刚才说 partial cancellation 是可能的 — 哪个对？"

### 5. 实时更新 CONTEXT.md

术语确定后立即更新，不批量处理。CONTEXT.md 只包含术语表，**不包含实现细节**。

### 6. 审慎地提供 ADR

只在以下**三个条件都满足**时才创建 ADR：

1. **难以逆转** — 改主意的成本很高
2. **没有上下文会让人惊讶** — 未来读者会问"为什么这样做"
3. **是真实权衡的结果** — 有真正的替代方案，你选了其中一个

少一个条件就跳过 ADR。

## CONTEXT.md 与 ADR 的关系

| | CONTEXT.md | ADR |
|--|-----------|-----|
| **内容** | 术语表（共享语言） | 架构决策（为什么这样做） |
| **包含** | 术语定义 + Avoid 词 | 上下文、决策、权衡、后果 |
| **更新频率** | 随时，实时 | 只在有重大决策时 |
| **实现细节** | ❌ 不包含 | ✅ 适当包含 |
| **谁读** | 人类和 AI | 人类和 AI |

## 常见陷阱

- ❌ **把实现细节塞进 CONTEXT.md** — 术语表是共享语言，不是 spec
- ❌ **批量更新** — 术语确定后要立即更新，不要攒一堆
- ❌ **过度 ADR** — 能改主意的简单决策不需要 ADR
- ❌ **不挑战用户** — 用户用模糊术语时不指出，后面会积累技术债
- ❌ **只问不查** — 事实性问题（"这个代码怎么写？"）自己去查，不要问用户