---
name: wizard
description: 交互式向导 — 生成 bash 脚本引导人类完成手动操作。
---

# Wizard Skill — 交互式 Bash 向导

源自 Matt Pocock 的 `wizard` 技能。生成一个交互式 bash 脚本，引导人类逐步完成手动操作 — 配置基础设施、设置凭据、操作第三方 dashboard、运行一次性迁移等。

## 触发场景

- 需要配置基础设施（云服务、数据库、CI/CD）
- 需要设置 API 凭据、密钥、OAuth
- 需要引导用户操作一个不熟悉的第三方 dashboard
- 需要运行一次性迁移或切换操作
- 用户说"这个步骤我手动做，你给我个脚本跟着走"

## 核心概念

**Wizard** 是一个 bash 脚本，包含：
- 多阶段逐步引导
- 自动打开浏览器跳转到需要的页面
- 捕获用户输入的值（公开展示或隐藏输入）
- 写入 `.env` 文件、GitHub Secrets 等
- 每个阶段确认，显示进度
- 结束时汇总

## 模板说明

使用 `template.sh` 作为基础模板，它提供了：
- 彩色的终端输出
- 跨平台打开浏览器（Linux/Mac/WSL）
- `ask` / `ask_secret` 输入捕获
- `write_env` 写入 `.env`
- `set_secret` / `set_var` 设置 GitHub Secrets
- `stage` / `say` / `step` 阶段控制
- 结束时汇总

## 流程

### 1. 确定操作步骤

列出所有手动步骤和每个步骤需要捕获的值。

**先读代码库**，不要白问：
- 配置文件：`.env`, `.env.example`, `docker-compose*`
- CI 配置：`.github/workflows/*` 中的 `secrets.*` / `vars.*`
- 文档：README, CONTRIBUTING.md

### 2. 和用户确认

展示按顺序排列的阶段列表和每个阶段产生什么值，让用户确认顺序。

### 3. 编写向导

从 template.sh 复制，替换阶段内容。每个阶段使用 `stage` / `say` / `step` / `open_url` / `ask` / `ask_secret` / `write_env` / `set_secret` 等辅助函数。

### 4. 验证

- `bash -n <script>` 检查语法
- `chmod +x <script>`
- 静态检查：每个值都有来源和去处

## 关键规则

1. **Wizard 是 ephemeral 的** — 默认一次性使用，保存到临时位置，完成后删除。只在用户要求时才提交到仓库
2. **打开浏览器在前，问值在后** — 先 open_url 打开页面，再 ask 问值
3. **secret 用 ask_secret** — 输入不显示在终端上
4. **不可逆操作前加 confirm** — 删除数据、迁移等操作前确认
5. **不要凭空编造步骤** — 不知道 UI 界面长什么样，就说明白并问用户

## 模板路径

template.sh 位于 `skills/software-development/wizard/template.sh` — 这是完整的 bash 向导库，创建时自动复制到 skill 目录中。

## 常见陷阱

- ❌ **不先读代码库就问用户** — `.env` 和 CI 配置告诉了你需要什么值
- ❌ **编造不存在的 UI 步骤** — 不知道就明说
- ❌ **不验证语法** — 写完后一定要 `bash -n`
- ❌ **把临时脚本提交到仓库** — 除非用户明确要求
- ❌ **不设置 `chmod +x`** — 脚本要可执行
- ❌ **secret 用 ask 而不是 ask_secret** — 密码不能在终端明文显示