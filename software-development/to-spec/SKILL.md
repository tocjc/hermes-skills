---
name: to-spec
description: 对话转 spec — 将当前讨论内容合成一份规范文档并发布。
---

# To-Spec Skill — 对话转规范文档

源自 Matt Pocock 的 `to-spec` 技能。把当前对话中的讨论内容合成一份结构化的 spec 文档，发布到 issue tracker 或本地文件。

## 触发场景

- 讨论已经充分，需要把结论写下来
- 需要一份正式的 spec 文档供团队参考
- 准备开始实现前，需要先确认 spec
- 用户说"把这些写成 spec"、"帮我整理成文档"

## 核心原则

**不访谈用户** — 只综合已有的讨论内容。如果信息不足，用 `grilling` 补，而不是在 `to-spec` 里问。

## Spec 模板

```
## Problem Statement
从用户视角描述当前面临的问题。

## Solution
从用户视角描述解决方案。

## User Stories
编号列表，格式：As a <角色>, I want <功能>, so that <价值>
尽量详尽，覆盖所有场景。

## Implementation Decisions
- 要构建/修改的模块
- 模块的接口
- 技术澄清
- 架构决策
- Schema 变更
- API 契约
- 具体交互逻辑

不包含具体文件路径或代码片段（容易过时）。
例外：如果 prototype 生成的代码片段比文字更精确，可以内联。

## Testing Decisions
- 什么构成好测试（只测外部行为，不测实现细节）
- 哪些模块需要测试
- 测试的 prior art（代码库中类似的测试）

## Out of Scope
明确不在此次范围内的内容。

## Further Notes
其他补充说明。
```

## 流程

### 1. 探索代码库

还没探索的话，先了解代码库的当前状态。使用项目的领域术语。

### 2. 确定测试 seam

画出要在哪些 seam 处测试。优先使用已有的 seam，尽量少的新 seam。理想情况下只用一个 seam。

### 3. 写 spec

使用上面的模板，然后发布到 issue tracker 或本地文件。

## 与 Hermes 技能配合

- `to-spec` 产出 spec → 然后 `plan` 或 `plan-implement-review` 执行
- 如果需求还不清晰，先用 `grilling` 梳理
- 写作时用 `domain-modeling` 的词汇表

## 常见陷阱

- ❌ **在 to-spec 里访谈用户** — to-spec 只综合，不访谈
- ❌ **包含文件路径和代码片段** — 容易过时
- ❌ **不写 Out of Scope** — 明确不做什么和做什么一样重要
- ❌ **用户故事太少** — 应该覆盖所有核心场景