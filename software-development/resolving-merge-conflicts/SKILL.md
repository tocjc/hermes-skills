---
name: resolving-merge-conflicts
description: 合并冲突解决 — 按意图逐块解决 git merge/rebase 冲突，永不 --abort。
---

# Resolving Merge Conflicts Skill — 合并冲突解决

源自 Matt Pocock 的 `resolving-merge-conflicts` 技能。系统化解决 git merge 或 rebase 冲突，逐个 hunk 处理，**永不 `--abort`**。

## 触发场景

- 用户说"合并冲突了，帮我解决"
- 正在做 git merge 或 rebase，遇到冲突
- 用户说"rebase 到 main 有冲突"

## 流程

### 1. 查看当前状态

- `git status` — 看哪些文件有冲突
- `git log --oneline` — 看当前分支和目标的 commit 历史
- 读取冲突文件 — 看每个冲突的内容

### 2. 找原始来源

对每个冲突 hunk，深挖两侧变更的来源：
- **读 commit message** — 每个变更为什么做
- **查 PR/issue** — 原始需求是什么
- **理解意图** — 不要只看代码，要理解为什么

### 3. 逐个解决

每个 hunk：
- **尽量保留双方意图** — 两者都合理时，合并
- **不兼容时** — 选与 merge 目标一致的一方，备注 trade-off
- **不要发明新行为** — 只做合并，不做新功能
- **永不 `--abort`** — 要么解决，要么停在那等待输入

### 4. 运行自动检查

- 类型检查
- 测试
- 格式化
- 修复 merge 带来的问题

### 5. 完成 merge/rebase

- Stage 所有文件
- Commit（merge 自动 commit，rebase 继续 `git rebase --continue`）

## 关键规则

- **永不 `--abort`** — 冲突解决不了就放着，不要重置
- **理解意图** — 读 commit message 和 PR，不要只看 diff
- **不发明新行为** — 合并冲突的解决不是新功能开发
- **先跑检查** — 解决完要验证类型和测试

## 常见陷阱

- ❌ **只看代码不看意图** — 读 commit message 和 PR
- ❌ **发明新行为** — 只合并，不开发
- ❌ **不跑检查** — 解决完要跑测试和类型检查
- ❌ **abort 了事** — 永不 abort，解决不了就放着等用户输入