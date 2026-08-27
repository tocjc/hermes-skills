---
name: wayfinder
description: 大型工作规划 — 决策地图 + 迷雾战争，多 session 复杂项目规划。
---

# Wayfinder Skill — 大型工作规划

源自 Matt Pocock 的 `wayfinder` 技能。当任务太大、一个 session 装不下，且路径不清晰时，用**决策地图 (Map)** 来探路。

## 触发场景

- 任务太大，远超一个 session 能完成
- 路径不清晰，需要先做决策再推进
- 需要多轮讨论才能确定实现方案
- 用户说"这个项目太大了，帮我规划一下"
- 涉及多个独立决策点，需要分步解决

## 核心概念

**Destination (目的地)** — 地图的终点。可能是一个 spec、一个决策、或一个变更。

**Map (地图)** — 一张 issue，标记 `wayfinder:map`，列出所有决策和进度。

**Decision Ticket (决策票)** — 子 issue，每个解决一个具体问题，类型为 research / prototype / grilling / task。

**Fog of War (迷雾战争)** — 还看不清的未知区域，记在 Map 的 "Not yet specified" 中。

**Frontier (前沿)** — 当前所有前置条件已满足、可以开始处理的 ticket。

## 地图结构

```
## Destination
<到达终点时的样子 — 一两句话>

## Notes
<领域、技能、偏好>

## Decisions so far
- [<已关闭的 ticket 标题>](link) — <答案摘要>

## Not yet specified
<还看不清的问题，待前沿推进后细化>

## Out of scope
<明确排除在本次工作范围之外的内容>
```

## Ticket 类型

| 类型 | 需要人 | 用途 |
|------|--------|------|
| **Research** | AFK(自动) | 查文档、查 API、查知识库，由 subagent 自动完成 |
| **Prototype** | HITL(需人) | 做个原型看看效果，用户参与讨论 |
| **Grilling** | HITL(需人) | 对话讨论，默认类型 |
| **Task** | 两者 | 必须先完成的体力活（注册服务、配置权限等） |

## 流程

### 1. 创建地图 (Chart the map)

1. **命名目的地** — 用 `grilling` 和 `domain-modeling` 确定地图要找什么
2. **广度优先扫描** — 先展开整个空间，弄清所有开放决策
3. **创建地图 issue** — 填写 Destination、Notes、Not yet specified
4. **创建可确定的 ticket** — 先创建，再连 blocking 关系
5. **启动 Research subagent** — 并行处理 research 类型的 ticket

### 2. 推进地图 (Work through the map)

1. 加载地图，看当前 frontier
2. **选中一个 ticket** — 或用户指定，或自动取 frontier 上第一个
3. **Claim it** — 分配给自己，避免冲突
4. **解决它** — 用对应的技能（grilling/research/prototype）
5. **记录结果** — 关闭 ticket，更新 Decisions so far
6. **暴露新 ticket** — 从迷雾中毕业新的可确定问题

## 关键规则

- **一次 session 只解决一个 ticket**（research 类型除外，可并行）
- **Plan, don't do** — 默认只做决策，不执行（除非 Notes 明确说可以）
- **用名称引用** — 引用 ticket 时用标题，不用编号
- **体验型调用** — 用 `delegate_task` 并行处理 research ticket

## 与 Hermes 技能配合

- 创建地图时调用 `grilling` 做需求访谈
- 创建地图时调用 `domain-modeling` 打磨术语
- 解决 ticket 时调用 `grilling` 做设计讨论
- 解决 research ticket 时用 `delegate_task` 自动查资料

## 常见陷阱

- ❌ **一次解决多个 ticket** — 一个 session 只做一个
- ❌ **把能做的也放进去** — 如果路径已经清晰，不需要地图
- ❌ **不标记 blocking** — 必须标注依赖关系，否则 frontier 是乱的
- ❌ **用编号引用** — 用标题，数字看不清
- ❌ **迷雾里硬创建 ticket** — 看不清就先记在 Not yet specified 里