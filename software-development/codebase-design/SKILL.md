---
name: codebase-design
description: 深度模块设计 — 设计小接口大行为的深模块，含 seam/leverage/locality 词汇。
---

# Codebase Design Skill — 深度模块设计

源自 Matt Pocock 的 `codebase-design` 技能。提供一套完整的词汇体系和设计原则，用于设计**深度模块 (Deep Modules)**：大量行为隐藏在小型接口背后，放置在干净的 seam 处，通过接口可测试。

## 触发场景

- 设计或改进模块的接口
- 寻找代码深化的机会
- 决定在哪里放置 seam/边界
- 让代码更可测试或 AI 可导航
- 在代码审查中讨论模块结构
- 用户说"这个模块太复杂了"、"接口太胖了"

## 核心词汇

使用这些术语要精确，不要替换成 "component"、"service"、"API"、"boundary"：

| 术语 | 定义 | 避免 |
|------|------|------|
| **Module** | 任何有接口和实现的东西。函数、类、包、跨层切片都可以 | unit, component, service |
| **Interface** | 调用者必须知道才能正确使用模块的所有信息：类型签名、不变式、顺序约束、错误模式、配置需求、性能特征 | API, signature |
| **Implementation** | 模块内部的代码体 | — |
| **Depth** | 接口的杠杆率：调用者每学一个接口单元，能获得多少行为 | — |
| **Seam** (Michael Feathers) | 可以在不修改该位置的情况下更改行为的地方 | boundary |
| **Adapter** | 在 seam 处满足接口的具体实现 | — |
| **Leverage** | 调用者从深度获得的好处：更多能力/接口学习量 | — |
| **Locality** | 维护者从深度获得的好处：变更、bug、知识、验证集中在一处 | — |

## 深模块 vs 浅模块

```
深模块 = 小接口 + 大实现
┌──────────────────────┐
│    Small Interface    │  ← 少方法、简单参数
├──────────────────────┤
│                      │
│  Deep Implementation │  ← 复杂逻辑隐藏在内
│                      │
└──────────────────────┘

浅模块 = 大接口 + 小实现（避免）
┌──────────────────────────────────┐
│      Large Interface              │  ← 多方法、复杂参数
├──────────────────────────────────┤
│  Thin Implementation              │  ← 只是透传
└──────────────────────────────────┘
```

## 设计原则

### 1. 深度是接口的属性，不是实现的属性

一个深模块内部可以由多个可 mock、可替换的小部件组成 — 它们只是不在接口里。

### 2. 删除测试

假设删除这个模块。如果复杂性消失了，它是透传。如果复杂性重新出现在 N 个调用者中，它在赚它的工资。

### 3. 接口就是测试面

调用者和测试跨越同一个 seam。如果你想测试"绕过"接口，模块的形状可能不对。

### 4. 一个 adapter = 假设的 seam，两个 adapter = 真正的 seam

除非有东西真的在变化，否则不要引入 seam。

## 设计接口时的检查清单

- 能减少方法数量吗？
- 能简化参数吗？
- 能把更多复杂性隐藏在内吗？

## 可测试性设计

### 接受依赖，不创建依赖

```
// 可测试
function processOrder(order, paymentGateway) {}

// 难测试
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

### 返回结果，不产生副作用

```
// 可测试
function calculateDiscount(cart): Discount {}

// 难测试
function applyDiscount(cart): void {
  cart.total -= discount;
}
```

### 小接口面

更少的方法 = 更少的测试。更少的参数 = 更简单的测试设置。

## 关系总结

```
Module ──has──▶ Interface
Module ──has──▶ Depth (属性)
Interface ──lives at──▶ Seam
Seam ──has──▶ Adapter (满足接口)
Depth ──produces──▶ Leverage (调用者)
Depth ──produces──▶ Locality (维护者)
```

## 与其他技能配合

- `codebase-design` 提供词汇 → 用于 `code-review` 的 Standards 审查
- `codebase-design` 的设计原则 → 用于 `plan-implement-review` 的模块设计阶段
- 与 `domain-modeling` 配合：领域建模确定术语，深度模块设计确定结构

## 常见陷阱

- ❌ **把"interface"等同于 TypeScript 的 interface 关键字** — 这里 Interface 包括调用者必须知道的全部信息
- ❌ **过早引入 seam** — 没有两个 adapter 就不需要 seam
- ❌ **用"depth"作为实现行数/接口行数比** — 那是 Ousterhout 的原始定义，我们用 depth-as-leverage
- ❌ **浅模块不重构** — 透传式模块积累多了就是泥球