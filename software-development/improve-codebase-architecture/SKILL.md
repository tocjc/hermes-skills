---
name: improve-codebase-architecture
description: 代码架构扫描 — 发现浅模块深化机会，生成 HTML 报告并讨论。
---

# Improve Codebase Architecture Skill — 代码架构扫描

源自 Matt Pocock 的 `improve-codebase-architecture` 技能。扫描代码库，发现架构摩擦点，提出**深化机会** — 把浅模块变成深模块的 refactor 方案。

## 触发场景

- 代码库感觉越来越乱，需要架构审视
- 用户说"看看这个模块能不能重构"、"代码太耦合了"
- 定期代码库健康检查（建议每几天跑一次）
- 准备大功能开发前，先看看架构是否需要调整

## 核心工具

依赖 `codebase-design` 技能的词汇体系：
- **Module, Interface, Depth, Seam, Adapter, Leverage, Locality**
- 删除测试、接口即测试面、一个 adapter 是假设的 seam

## 流程

### 1. 探索

**YAGNI 先确定范围**。把精力放在最近频繁变更的区域：

- 如果用户指定了方向，直接去
- 否则看 `git log --oneline` 找热点区域
- 先读 `CONTEXT.md` 和 ADR

然后用 subagent 走查代码，关注：
- 理解一个概念需要跳转多个模块？
- 模块**浅**（接口几乎和实现一样复杂）？
- 纯函数为了可测试性被提取出来，但真实 bug 藏在调用方式中？
- 紧耦合模块跨 seam 泄漏？
- 哪些部分没有测试，或难以通过接口测试？

**删除测试**：怀疑某个模块浅时，假设删除它。如果复杂性消失，它只是透传；如果复杂性重新出现在 N 个调用者中，它在赚工资。

### 2. 生成 HTML 报告

写一个自包含的 HTML 文件到临时目录（用 `delegate_task` 生成）。每个候选以卡片形式展示：

- **Files** — 涉及的文件/模块
- **Problem** — 当前架构为什么有摩擦
- **Solution** — 要改什么
- **Benefits** — 用 locality 和 leverage 表述
- **Before / After 图** — 用 Mermaid 或手绘 SVG
- **Recommendation** — Strong / Worth exploring / Speculative

### 3. 讨论

用户选一个候选后，用 `grilling` 讨论决策树。

## 与 Hermes 技能配合

- `improve-codebase-architecture` 发现机会 → 用 `grilling` 讨论
- 讨论中调用 `domain-modeling` 更新术语
- 用 `codebase-design` 的词汇精确描述
- 确定方案后，用 `plan` 或 `plan-implement-review` 执行

## 常见陷阱

- ❌ **扫描整个代码库** — 先确定范围，找热点区域
- ❌ **不提建议** — 只有发现没有方案是没有意义的
- ❌ **不画 before/after 图** — 可视化帮助理解
- ❌ **不排优先级** — 总要有一个 Top recommendation
- ❌ **不尊重 ADR** — 和现有 ADR 冲突时需要标注