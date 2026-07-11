---
name: skill-eval
license: MIT
description: |
  评估和迭代技能（SKILL.md）效果的编排方法论。用于以下场景：
  - 创建新技能后需要验证它是否有效
  - 修改现有技能后需要对比效果
  - 需要定量/定性评估技能带来的质量提升
  - 优化技能触发（description）的准确性
  包含：eval 测试用例设计、with-skill vs baseline 子 Agent 并行跑分、定量断言评分、
  定性人工审阅、迭代闭环、技能描述优化触发测试。
  借鉴自 Anthropic skill-creator 的 eval 方法论。

  不适用：不需要评估技能的普通任务、非 Hermes Agent 的技能开发。
metadata:
  origin: https://github.com/anthropics/skills/tree/main/skills/skill-creator
  version: "1.0"
---

# Skill Evaluation方法论

## 核心流程

```
创建/修改技能 → 写 eval 测试用例 → 子 Agent 并行跑分 → 评估结果 → 改进技能 → 循环
```

## 阶段 0：理解技能意图

在开始评估前，先理解技能要解决什么问题。

1. **该技能让 AI 能做什么以前不能做的事？** 核心价值是什么
2. **触发条件是什么？** 用户的哪些说法/场景应该激活这个技能
3. **预期输出是什么？** 格式、质量、行为标准
4. **输出是否可以**客观验证 **？**（文件转换、数据提取、代码生成 → 适合定量 eval；写作风格、创意设计 → 适合定性 eval）

## 阶段 1：设计 Eval 测试用例

### 1.1 创建 eval 数据集

在技能目录下创建 `evals/evals.json`：

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "name": "描述性名称",
      "prompt": "用户会说的真实任务——要有细节、上下文，像真人说的话",
      "expected_output": "预期的结果描述",
      "files": [],
      "assertions": []
    }
  ]
}
```

### 1.2 写好 test prompts

**好 prompt 的标准：**
- 像真实用户说的话：有细节、上下文、甚至有小错误
- 不是"帮我做 X"这种单行命令，而是有场景的请求
- 覆盖边缘情况：不同格式、不同复杂度

**坏例子：** `"读取这个PDF"`
**好例子：** `"我老板刚发了我一个 PDF（在我的下载文件夹里，叫 Q4-final-report.pdf），里面有个表格列出了竞争对手的定价。帮我把那个表格提取出来转成 Excel，我要对比一下。"`

写 2-5 个 test cases，覆盖技能的不同方面。如果技能有多种使用方式，每个方式至少一个 test case。

### 1.3 设计定量断言（可选）

对于可客观验证的输出，设计断言：

```json
{
  "assertions": [
    {
      "name": "文件扩展名正确",
      "check": "output 文件以 .xlsx 结尾"
    },
    {
      "name": "包含了必需列",
      "check": "Excel 中有 Revenue 和 Cost 列"
    },
    {
      "name": "公式优先",
      "check": "占比列是 Excel 公式而非硬编码值"
    }
  ]
}
```

好的断言：**客观可验证**，名称清晰到一看就懂在检查什么。

**主观技能的评估（写作风格、设计质量）不适合定量断言**——靠人工定性审阅。

## 阶段 2：并行跑分

### 2.1 同时启动 with-skill 和 baseline

**这一步的关键：同时启动，不串行。** 用 `delegate_task` 在同一个 turn 里启动所有子 Agent。

对于每个 test case，启动两个子 Agent：
- **With-skill run**：加载要评估的技能来执行
- **Baseline run**：不加载技能（或加载旧版本技能）

```javascript
// 同时启动所有子 Agent
const tasks = [];
for (const eval of evals) {
  tasks.push({
    goal: `执行以下任务：\n${eval.prompt}\n\n保存结果到 /tmp/skill-eval/iteration-N/eval-${eval.id}/with_skill/\n将最终产物的路径写在结果摘要中`,
    context: `按照 ${skill_name} 技能的指引来完成任务。`,
    toolsets: ['terminal', 'file', 'web']
  });
  tasks.push({
    goal: `执行以下任务：\n${eval.prompt}\n\n保存结果到 /tmp/skill-eval/iteration-N/eval-${eval.id}/without_skill/\n将最终产物的路径写在结果摘要中`,
    context: `不使用任何特定技能，用你的一般能力完成。`,
    toolsets: ['terminal', 'file', 'web']
  });
}
```

**批次限制：** 每个用户最多同时 3 个并发子 Agent。如果有 3 个 test cases 就是 6 个任务，分 2 批启动。

### 2.2 记录 timing 数据

子 Agent 完成后，结果中包含 `total_tokens` 和 `duration_ms`。立即保存到每个运行目录的 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是唯一能采集到这些数据的时机——来自子 Agent 返回的结果。

## 阶段 3：评估结果

### 3.1 定量评分

为每个 test case 创建 grader 子 Agent，检查断言是否通过：

```
goal: `评估以下输出是否符合断言标准。
输出路径：/tmp/skill-eval/iteration-N/eval-${eval.id}/with_skill/outputs/
断言列表：${JSON.stringify(eval.assertions, null, 2)}

对每条断言，检查：
1. 是否通过（passed: true/false）
2. 证据是什么（evidence: 具体观察到的内容）

返回 JSON 格式的评分结果。`
```

保存结果到 `grading.json`：

```json
{
  "assertions": [
    {"text": "文件扩展名正确", "passed": true, "evidence": "输出文件为 output.xlsx"},
    {"text": "包含了必需列", "passed": true, "evidence": "文件中包含 Revenue 和 Cost 列"},
    {"text": "公式优先", "passed": false, "evidence": "占比列使用了硬编码值 0.15，而非公式"}
  ]
}
```

**对于可以程序化检查的断言**，写个脚本跑而不是目测——更快、更可靠、可复用。

### 3.2 汇总 benchmark

制作 benchmark 汇总表，包含每个 test case 的 with-skill vs baseline 对比：

| Test Case | With-Skill | Baseline | Δ |
|-----------|-----------|----------|---|
| Eval 1: 提取表格 | ✅ 3/3 pass | ❌ 1/3 pass | +2 |
| Eval 2: 创建报告 | ✅ 2/2 pass | ✅ 2/2 pass | 0 |
| Eval 3: 格式转换 | ✅ 2/3 pass | ❌ 0/3 pass | +2 |
| **总计** | **7/8 (87%)** | **3/8 (37%)** | **+50%** |

同时记录 token 消耗和时间：

| Test Case | With-Skill Tokens | Baseline Tokens | With-Skill Time | Baseline Time |
|-----------|------------------|-----------------|----------------|---------------|
| Eval 1 | 84,852 | 45,233 | 23.3s | 12.1s |

### 3.3 Analyst 分析

浏览 benchmark 数据，寻找汇总统计可能掩盖的模式：

1. **非区分性断言** — with-skill 和 baseline 都通过/都不通过的断言 → 说明这个断言没有区分度
2. **高方差 evals** — 多次运行结果不一致 → 可能是 flaky
3. **时间/Token 权衡** — 技能提升质量但消耗更多 token？这是否合理？
4. **pattern 发现问题** — 所有 baseline 在某类任务上都失败了 vs 所有 with-skill 都成功

### 3.4 生成审阅报告

将结果写入 `/tmp/skill-eval/report.md`，包含：

- 每个 test case 的 prompt 和产出摘要
- 定量评分汇总表
- with-skill vs baseline 的对比
- Analyst 发现的问题
- 改进建议

然后向用户展示报告，请求反馈。

### 3.5 定性用户审阅

向用户展示结果，请求反馈。好的做法是：

> "这是第一轮结果。定量上看技能提升了 X%，但有几个方面想听听你的意见：
> 1. Eval 1 的输出质量你满意吗？
> 2. Eval 2 中 baseline 也成功了，你觉得技能在这种情况下是过度设计了还是在某些微妙的地方更好？
> 3. 有什么你注意到的问题是我没捕捉到的？"

**对于可直观比较的输出**（图片、HTML渲染、文档），将产物路径告诉用户让他们自己看。

## 阶段 4：迭代改进

### 4.1 如何思考改进

1. **从反馈中抽象**：不要只修这一个 test case 暴露的问题，要想到这个技能会被用一百万次。修根不修表。
2. **精简 prompt**：去掉不干活的指令。如果技能让模型浪费大量时间做无用功，砍掉那些部分。
3. **解释为什么**：比起用 ALL CAPS 的 MUST/NEVER，更好的方式是把背后的为什么说清楚。今天的 LLM 很聪明，理解意图后能做得更好。
4. **找重复工作**：读跑分时的 transcript，如果所有子 Agent 都独立写了相似的 helper 脚本，说明技能应该自带这个脚本。
5. **防止过拟合**：如果你只对着 2-3 个 test case 反复优化，很容易做出只对这 2-3 个例子有效的东西。偶尔换一批 test case 或加大难度。

### 4.2 迭代循环

```
1. 应用改进到 SKILL.md
2. 重新跑所有 test case 到 iteration-<N+1>/ 目录
3. 报告新结果，和上一轮对比
4. 等待用户反馈
5. 读新反馈，改进，重复
```

**什么时候停止：**
- 用户说满意了
- 反馈都是空的（说明看起来都不错）
- 连续两轮没有有意义的进步

## 阶段 5：进阶：技能描述优化

skill 的 `description` 字段是决定 AI 是否调用该技能的主要机制。创建/改进技能后，可以优化 description 以提高触发准确性。

### 5.1 生成触发测试查询

创建 20 个 eval queries —— 混合应该触发和不应该触发的：

```json
[
  {"query": "可以帮我把这个 PDF 里的表格提取出来吗？表格从第 3 页开始，有个产品价格对比表", "should_trigger": true},
  {"query": "帮我把这个 Python 代码 review 一下，看有什么安全问题", "should_trigger": false}
]
```

**原则：**
- **应该触发的（8-10个）**：不同说法表达同一意图——正式、随意、带有语境
- **不应该触发的（8-10个）**：最有价值的是**接近但不触发**的情形——共享关键词但实际不需要该技能
- 查询要有细节：文件路径、公司名、列名、URL、个人背景
- 覆盖边缘情况，不要做明显区分

**坏例子：** `"读取这个PDF"` `"格式化数据"` — 太简短，不会触发技能
**好例子：** `"我老板刚发了个 PDF...里面有表格..."` — 有上下文，更像真人说的

### 5.2 触发测试跑分

为每个 query 启动子 Agent，在指令中**不指定技能也不禁止技能**：
- 目标标记为 `should_trigger: true` 的：检查子 Agent 是否主动加载了目标技能
- 目标标记为 `should_trigger: false` 的：检查子 Agent 是否没有加载目标技能

将结果记录到表格：

| Query | 期望触发 | 实际触发 | 结果 |
|-------|---------|---------|------|
| 提取 PDF 中的表格 | ✅ | ✅ | ✅ 命中 |
| 写一个 Python 爬虫 | ❌ | ❌ | ✅ 正确拒绝 |
| ... | | | |

### 5.3 优化 description

基于触发测试结果，调整 description：

- 如果 should_trigger 的没触发 → description 缺少关键触发词
- 如果 shouldn't_trigger 的触发了 → description 边界不清晰，有歧义
- 修改后重新跑触发测试，直到准确率达到 90%+

**触发行为理解：** AI 只会在**自己处理不了**或**有明确的 specialized skill** 时才调用 skill。短的单步查询（如"读这个 PDF"）即使 description 匹配得好也可能不触发，因为 AI 认为它能直接用工具处理。所以测试查询要有足够的复杂度。

### 5.4 应用优化

修改 SKILL.md 的 description 字段，展示 before/after 对比，并报告准确率从多少提升到了多少。

## 完整工作流速查

```
创建技能初版
    ↓
写 2-5 个 eval test cases (evals/evals.json)
    ↓
设计定量断言（可客观验证的输出）或跳过（主观类技能）
    ↓ ────────────── 并行 ──────────────
启动所有 with-skill 子 Agent    启动所有 baseline 子 Agent
    ↓                              ↓
等待完成，记录 timing 数据        等待完成，记录 timing 数据
    ↓ ────────────── 汇总 ──────────────
定量评分 (grading.json)
汇总 benchmark 表格
Analyst 分析
生成报告 (report.md)
    ↓
向用户展示结果，获取反馈
    ↓
改进技能 SKILL.md
    ↓
回到"写 eval test cases"循环
    ↓
（可选）当技能稳定后：优化 description 触发准确性
```

## 目录结构约定

```
skills/my-skill/
├── SKILL.md              # 技能本身
├── evals/
│   ├── evals.json        # eval 数据集（test prompts + assertions）
│   └── trigger-eval.json # description 触发测试（可选）
└── iteration-1/           # 第一轮结果（每次跑分生成）
    ├── eval-1/
    │   ├── with_skill/
    │   │   ├── outputs/   # 产物
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── eval-2/
    │   └── ...
    ├── benchmark.md       # 汇总表格 + 分析
    └── report.md          # 向用户展示的报告
```

## 常见陷阱

1. **不要串行跑分** — With-skill 和 baseline 必须同时启动，否则先跑的结果可能影响你对另一个的判断
2. **不要把 timing 放跑后再说** — 子 Agent 返回时立刻记录 timing，只有那一次机会
3. **不要只用定量数据做决定** — 定量的"通过"不代表质量好，让用户看看产物的实际效果
4. **不要过拟合 test cases** — 如果只对着 2 个例子反复改，改出来的技能可能只对这 2 个例子有效
5. **不要把评估者和技能写在一起** — 评估者不用加载目标技能，否则会污染 AI 的行为
6. **不要跳过 baseline** — 不看 baseline 你就不知道技能到底有没有带来提升
7. **description 不是越长越好** — 在完整和精确间找平衡，优先包含触发关键词