---
name: to-tickets
description: 计划拆任务 — 将 spec 或对话拆成 tracer-bullet 垂直切片任务。
---

# To-Tickets Skill — 计划拆分为任务

源自 Matt Pocock 的 `to-tickets` 技能。把 plan、spec 或当前对话拆成一组 **tracer bullet 垂直切片**任务，每个任务标注其 blocking 依赖关系。

## 触发场景

- 需要一个 spec 或计划的执行步骤清单
- 需要把大任务拆成可独立完成的小任务
- 准备开始编码前，需要任务拆分
- 用户说"帮我拆成 tickets"、"分解任务"

## 核心概念

**Tracer bullet 垂直切片** — 每个切片从数据库到前端切一条完整的路径，完成后可独立演示/验证。

**Blocking 依赖** — 每个 ticket 标注它依赖哪些其他 ticket。

**Frontier** — 当前所有依赖已满足、可以开始做的 ticket。

**Wide refactor** — 影响范围横跨整个代码库的机械性变更（如重命名列、改类型定义），用 **expand-contract** 模式处理。

## 流程

### 1. 收集上下文

从当前对话中提取信息。如果用户传了 spec 路径或 issue 号，去获取。

### 2. 探索代码库

了解当前代码状态。使用项目领域术语，尊重 ADR。

### 3. 拆分垂直切片

**垂直切片规则**：
- 每个切片切穿所有层（schema、API、UI、测试）— 垂直，不是水平切片
- 一个完成的切片可以独立演示或验证
- 每个切片的大小适配一个 session
- 先做 prefactoring

**Wide refactor 例外**：用 expand-contract 模式：
1. **Expand** — 新形式放在旧形式旁，不破坏任何东西
2. **Migrate** — 按影响范围分批迁移调用点
3. **Contract** — 所有调用点迁移完成后删除旧形式

### 4. 和用户确认

展示拆分方案。每个 ticket 显示：
- **标题**: 简短描述
- **Blocked by**: 依赖哪些其他 ticket
- **交付物**: 这个 ticket 完成后什么功能可用

### 5. 发布

发布到 issue tracker 或本地文件。按依赖顺序发布（blocker 先发）。

## 本地文件格式

```
.scratch/<feature-slug>/issues/
├── 01-<slug>.md   ← 无依赖，可先开始
├── 02-<slug>.md   ← Blocked by: 01
└── 03-<slug>.md   ← Blocked by: 02
```

每个 ticket 模板：
```
# <NN> — <Title>

**What to build:** 端到端行为描述

**Blocked by:** <依赖的 ticket 编号/title，或 None>

**Status:** ready-for-agent

- [ ] 验收标准 1
- [ ] 验收标准 2
```

## 常见陷阱

- ❌ **水平切片** — 每个 ticket 应该是垂直的完整路径
- ❌ **不标注 blocking** — 依赖关系决定了执行顺序
- ❌ **ticket 太大** — 一个 ticket 应该适配一个 session
- ❌ **不考虑 wide refactor** — 大规模机械变更需要 expand-contract
- ❌ **不确认用户** — 拆分方案必须和用户对齐