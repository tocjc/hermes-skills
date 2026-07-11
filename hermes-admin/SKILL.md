---
name: hermes-admin
description: "Hermes Agent 环境管理: 技能库备份/恢复/迁移、目录导出、git 管理、环境状态检查。适用于迁移到新机器、定期存档、技能库文档化、环境一致性检查。"
---

# Hermes Admin

Hermes Agent 环境管理：备份、恢复、迁移、目录导出和状态检查。

> **适用场景**：用户要求备份技能、迁移环境、导出技能目录、检查 Hermes Agent 状态、管理技能库的 git 仓库

## 环境概览

| 路径 | 说明 |
|------|------|
| `~/.hermes/skills/` | 技能库（SKILL.md + 附属脚本/模板/引用） |
| `~/.hermes/memories/` | 内存（跨会话记忆） |
| `~/.hermes/config.yaml` | 主配置 |
| `~/.hermes/cron/` | 定时任务 |
| `~/.hermes/plugins/` | 插件 |

## 技能库备份

### 方式一：Git 仓库（推荐）

```bash
cd ~/.hermes/skills

# 初始化（首次）
git init
git add .
git commit -m "初始技能库"

# 配置远程
git remote add origin <remote-url>
git push -u origin master

# 日常增量备份
git add -A
git commit -m "更新技能 $(date +%F)"
git push
```

**Secure token authentication via `git credential approve`** (no token in command args):

```bash
printf "protocol=https\nhost=github.com\nusername=<user>\npassword=<ghp_token>\n" | git credential approve
git config --global user.name "<user>"
git config --global user.email "<user>@users.noreply.github.com"
git remote set-url origin https://github.com/<user>/hermes-skills.git
```

**Create the remote repo via GitHub API** (if it doesn't exist yet):

```bash
GITHUB_TOKEN=***  # Use env var, NOT inline in command text
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -X POST https://api.github.com/user/repos \
  -d '{"name":"hermes-skills","private":false,"description":"Hermes Agent 技能备份"}'
```

Then push with `git push -u origin main` (GitHub defaults to `main`, not `master`).

**Multi-machine sync:**

| Step | Machine A | Machine B |
|------|-----------|-----------|
| 1 | `git push` | — |
| 2 | — | `git pull` |
| 3 | — | Restart Hermes session (skills auto-load) |

### 方式二：tar.gz 压缩包（便携存档）

```bash
tar czf hermes-skills-$(date +%Y%m%d).tar.gz \
  -C ~/.hermes skills/
```

### 方式三：选择性打包（仅 SKILL.md）

```bash
cd ~/.hermes/skills
find . -name "SKILL.md" | tar czf hermes-skills-light-$(date +%Y%m%d).tar.gz -T -
```

## 技能目录导出

生成结构化 Markdown 技能清单：

```bash
hermes skills list > /tmp/skills-catalog.md
```

或者通过 agent 调用 skills_list() 工具获取完整 JSON，再按分类组织成可读文档。

导出内容按以下结构组织：
1. 按 category 分组
2. 每个技能含 name + description
3. 标注计总数

## 技能库恢复

```bash
cd ~/
rm -rf .hermes/skills-bak
mv ~/.hermes/skills ~/.hermes/skills-bak

# 从 git 恢复
git clone <remote-url> ~/.hermes/skills

# 从 tar.gz 恢复
tar xzf hermes-skills-20250101.tar.gz -C ~/.hermes/
```

## 环境检查

```bash
# 技能数量
find ~/.hermes/skills -name "SKILL.md" | wc -l

# 技能库总大小
du -sh ~/.hermes/skills/

# 附属文件统计（非 SKILL.md）
find ~/.hermes/skills -not -name "SKILL.md" -type f | wc -l

# 最近修改的技能
find ~/.hermes/skills -name "SKILL.md" -newer /tmp/skills-ref -ls 2>/dev/null

# Git 状态（如果已初始化）
cd ~/.hermes/skills && git status --short
```

## 最佳实践

1. **定期备份** — 技能库在有意义的新技能添加后就应该备份
2. **双保险** — git 远程 + 本地 tar.gz 压缩包双重存档
3. **gitignore** — 技能目录的 `.gitignore` 应排除大文件/临时文件：
   ```
   .DS_Store
   __pycache__/
   *.pyc
   .venv/
   node_modules/
   .env
   *.log
   ```
4. **远程优先** — GitHub/GitLab/Gitee 作为主备份，tar.gz 做离线存档
5. **目录文档化** — 每次备份时顺便更新目录清单，方便检索
6. **恢复验证** — 备份后验证 `hermes skills list` 输出与原库一致

## Pitfalls

### ❌ GitHub token revocation

**Symptom**: First `git push` succeeds, subsequent pushes fail with `Bad credentials`; GitHub API returns 401.

**Cause**: Token appeared in command-line text (e.g., `echo "https://user:token@github.com" > ~/.git-credentials`). GitHub security scanner detected it and auto-revoked the token.

**Prevention**: Use `git credential approve` via stdin (see 方式一 above) — token NEVER enters the command arguments or shell history visible to the scanner.

### ❌ `***` redaction eating the real token

**Symptom**: A security scanner replaces the token with `***` in terminal output, then a subsequent shell command writes the literal string `***` instead of the real token value.

**Lesson**: Once a token is redacted from the session, it's unrecoverable. You must ask the user to generate a fresh token. Never capture a redacted value and reuse it.

### ❌ Skills directory git history bloat

Skills directories often contain hundreds of SKILL.md files plus thousands of supporting files (~112MB total, ~50-80MB for `.git/`). The initial `git add .` and `git push` can take minutes. Consider splitting into smaller repos if the directory exceeds 500MB, or use `.gitignore` to exclude generated/large files (copy assets, compiled scripts).

## 参考

- 本技能目录导出脚本见 `references/skills-catalog.sh`，详细指南见 `references/skills-catalog-guide.md`
- GitHub 备份会话记录见 `references/session-backup-workflow.md`（含授权配置、token 安全注意事项和多机同步）
- 技能库通常 100-200 个 SKILL.md 文件，3300+ 附属文件，~112MB（含 .git/）