---
name: self-improving-agent
description: 捕获经验教训、错误和纠正，实现持续改进。使用时机：（1）命令或操作意外失败；（2）用户纠正你；（3）发现了更好的方法；（4）用户请求新功能；（5）反复出现同一问题。通过 .learnings/ 文件化日志 + Hermes memory/skill 工具双轨记录。
---

# Self-Improving Agent

捕获经验教训、错误和纠正，以实现持续改进。基于 pskoett 的 Self-Improving Agent (ClawHub)，适配到 Hermes Agent 环境。

## 核心理念

Hermes Agent 已有强大的记忆（`memory`）和技能（`skill_manage`）工具，但该技能补充的是：
- **项目级别的、文件化的日志系统**，适合团队共享和 git 追踪
- **更细粒度的优先级/分类/状态管理**
- **结构化模板**，便于后续搜索和批量处理

建议采用 **双轨策略**：
1. **跨会话持久知识**（用户偏好、环境事实、工具诀窍）→ `memory` 工具
2. **项目级可复用工作流** → `skill_manage` 工具
3. **项目内具体日志**（错误、纠正、功能请求）→ `.learnings/` 文件

## 首次初始化

在项目根目录创建 `.learnings/` 目录和文件：

```bash
mkdir -p .learnings
[ -f .learnings/LEARNINGS.md ] || printf "# Learnings\n\nCorrections, insights, and knowledge gaps captured during development.\n\n**Categories**: correction | insight | knowledge_gap | best_practice\n\n---\n" > .learnings/LEARNINGS.md
[ -f .learnings/ERRORS.md ] || printf "# Errors\n\nCommand failures and integration errors.\n\n---\n" > .learnings/ERRORS.md
[ -f .learnings/FEATURE_REQUESTS.md ] || printf "# Feature Requests\n\nCapabilities requested by the user.\n\n---\n" > .learnings/FEATURE_REQUESTS.md
```

不要覆盖已有文件。如果 `.learnings/` 已初始化，跳过此步骤。

不要记录密钥、令牌、私钥、环境变量或完整的源码/配置文件，除非用户明确要求。优先使用简短摘要或去敏的摘录。

## Quick Reference

| 场景 | 动作 |
|------|------|
| 命令/操作意外失败 | 记录到 `.learnings/ERRORS.md` |
| 用户纠正你 | 记录到 `.learnings/LEARNINGS.md`，分类 `correction` |
| 用户请求缺失功能 | 记录到 `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | 记录到 `.learnings/ERRORS.md`，附集成详情 |
| 知识过时 | 记录到 `.learnings/LEARNINGS.md`，分类 `knowledge_gap` |
| 发现更好的方法 | 记录到 `.learnings/LEARNINGS.md`，分类 `best_practice` |
| 简化/加固重复模式 | 更新 `.learnings/LEARNINGS.md`，标注 `Source: simplify-and-harden` 和稳定 `Pattern-Key` |
| 跟已有条目相似 | 添加 **See Also** 链接，考虑提升优先级 |
| 广泛适用的学习 | 提升到 memory 或 skill（见下方"提升机制"） |
| 用户要求备份/导出技能库 | 生成 skills-catalog.md + 推送到 GitHub（见 `references/skills-library-maintenance.md`） |
| 新技能持续增多 | 运行定期维护：清点数量、检查重复、更新 README 和 catalog |

## 日志格式

### 学习条目

追加到 `.learnings/LEARNINGS.md`：

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: YYYY-MM-DDTHH:MM:SSZ
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
一行描述学到的内容

### Details
完整上下文：发生了什么，什么错了，什么是对的

### Suggested Action
具体的修复或改进方案

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001
- Pattern-Key: simplify.dead_code | harden.input_validation

---
```

### 错误条目

追加到 `.learnings/ERRORS.md`：

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: YYYY-MM-DDTHH:MM:SSZ
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
简要描述什么失败了

### Error
```
实际的错误信息或输出
```

### Context
- 命令/操作尝试
- 输入或参数
- 环境详情（如相关）
- 相关输出的摘录（避免完整日志和密钥）

### Suggested Fix
如果可识别，可能的解决方案

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001

---
```

### 功能请求条目

追加到 `.learnings/FEATURE_REQUESTS.md`：

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: YYYY-MM-DDTHH:MM:SSZ
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
用户想做什么

### User Context
为什么需要它，解决什么问题

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
如何构建，可能扩展什么

### Metadata
- Frequency: first_time | recurring
- Related Features: existing_feature_name

---
```

## 提升机制（Promotion）

当学习被证明广泛适用时：

### 提升到 Hermes memory

广泛适用的**事实性知识**（用户偏好、环境事实、工具诀窍）→ 用 `memory` 工具保存

### 提升到 Hermes skill

**可复用的工作流**（经过验证的多步骤流程、修复模式）→ 用 `skill_manage` 保存

### 提升判定标准（全部满足时提升）

1. **Recurrence-Count >= 3**（重复出现3次以上）
2. **跨越至少2个不同任务**
3. **发生在30天内**

### 提升后更新条目

```
**Status**: pending → **Status**: promoted
**Promoted**: memory (key: xxx) | skill (name: xxx)
```

## 重复模式检测

如果记录的内容和已有条目相似：

1. 搜索已有：`grep -r "关键词" .learnings/`
2. 链接条目：在 Metadata 中添加 `**See Also**: ERR-20250110-001`
3. 如果问题持续出现，考虑提升 priority
4. 持续出现的问题往往意味着：
   - 缺少文档 → 提升到 skill
   - 缺少自动化 → 创建 cronjob 或 skill
   - 架构问题 → 创建技术债务条目

## 自动触发场景

在以下情况**自动**记录（无需等待用户提醒）：

### 纠正（→ `LEARNINGS.md`，分类 `correction`）
- 用户说："不对..."、"应该是..."、"你说错了..."、"那个过时了..."

### 功能请求（→ `FEATURE_REQUESTS.md`）
- 用户说："能不能..."、"我希望你能..."、"有没有办法..."

### 知识缺口（→ `LEARNINGS.md`，分类 `knowledge_gap`）
- 用户提供了你不知道的信息
- 你引用的文档已过时
- API 行为和你理解的不一致

### 错误（→ `ERRORS.md`）
- 命令返回非零退出码
- 出现异常或堆栈跟踪
- 意外输出或行为
- 超时或连接失败

## 最佳实践

1. **立即记录** — 在问题发生后的上下文最新鲜时
2. **具体** — 让未来的 agent 能快速理解
3. **包含复现步骤** — 尤其是对于错误
4. **链接相关文件** — 让修复更容易
5. **给出具体的修复建议** — 不仅仅是"调查一下"
6. **使用一致的分类** — 方便后续过滤
7. **积极提升** — 不确定是否提升时，优先提升
8. **定期回顾** — 过时的学习会失去价值
9. **维护技能库** — 定期生成 skills-catalog.md、推送到远程 repo（详见 [`references/skills-library-maintenance.md`](skills-library-maintenance.md)）

## Hermes 双轨记录对照

| 场景 | Hermes memory | skill_manage | .learnings/ 文件 |
|------|---------------|--------------|-------------------|
| 用户偏好/习惯 | ✅ 首选 | ❌ | ❌ |
| 环境/OS 事实 | ✅ 首选 | ❌ | ❌ |
| 工具诀窍 | ✅ 首选 | ❌ | ✅ 补充 |
| 可复用工作流 | ❌ | ✅ 首选 | ✅ 补充 |
| 单次错误日志 | ❌ | ❌ | ✅ 首选 |
| 功能请求追踪 | ❌ | ❌ | ✅ 首选 |
| 重复模式分析 | ❌ | ✅ 最终状态 | ✅ 中间状态 |