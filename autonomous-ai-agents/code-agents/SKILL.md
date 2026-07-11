---
name: code-agents
description: Delegate coding tasks to external AI coding agents via terminal — covers OpenAI Codex CLI and OpenCode CLI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [coding-agent, codex, opencode, automation, code-review, refactoring]
    related_skills: [claude-code, kanban-codex-lane, hermes-agent]
---

# External Coding Agents

Delegate coding tasks to external autonomous coding agent CLIs. This umbrella covers two agents with very similar patterns: **Codex CLI** (OpenAI) and **OpenCode CLI** (provider-agnostic, open-source).

For Claude Code (Anthropic), see the `claude-code` skill — it has a much richer CLI and separate orchestration patterns.

## Common Patterns Across All Agents

All external coding agents share these patterns:

- **`pty=true`** — interactive TUI apps require a PTY (but one-shot `exec`/`run` modes often don't)
- **Git repo required** — most agents refuse to run outside a git directory. Use `mktemp -d && git init` for scratch work
- **Isolated worktrees** — use `git worktree add` for parallel work in separate directories
- **Background mode** for long tasks: `background=true, pty=true`, monitor with `process(action="poll"|"log")`
- **Monitor progress** with `process(action="poll", session_id="<id>")` — don't sit idle
- **Always set `workdir`** — keep the agent focused on the right project directory
- **Cleanup** — remove temp worktrees when done

---

## Section A: Codex CLI (OpenAI)

Delegate coding tasks to [Codex](https://github.com/openai/codex) — OpenAI's autonomous coding agent CLI.

### Prerequisites

```bash
npm install -g @openai/codex
```

Auth: `OPENAI_API_KEY` or Codex OAuth credentials from the Codex CLI login flow.

### One-Shot Tasks

```bash
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```bash
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

### Background Mode (Long Tasks)

```bash
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

### Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

### PR Reviews

Clone to a temp directory for safe review:
```bash
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

### Parallel Issue Fixing with Worktrees

```bash
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor, then push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

---

## Section B: OpenCode CLI (Provider-Agnostic)

Use [OpenCode](https://opencode.ai) as an autonomous coding worker. Provider-agnostic, open-source.

### Prerequisites

```bash
npm i -g opencode-ai@latest
# or: brew install anomalyco/tap/opencode
```

Auth: `opencode auth login` or set provider env vars.

### Binary Resolution

If behavior differs between terminal and Hermes, check:
```bash
terminal(command="which -a opencode")
terminal(command="opencode --version")
```
If needed, pin an explicit binary path:
```bash
terminal(command="$HOME/.opencode/bin/opencode run '...'", workdir="~/project", pty=true)
```

### One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:
```bash
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach context files with `-f`:
```bash
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Force a specific model:
```bash
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

### Interactive Sessions (Background)

```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Exit cleanly — Ctrl+C (NOT /exit)
process(action="write", session_id="<id>", data="\x03")
```

**Important:** Do NOT use `/exit` — it opens an agent selector. Use Ctrl+C (`\x03`) or `kill`.

### Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last session |
| `--session <id>` / `-s` | Continue a specific session |
| `--model provider/model` | Force specific model |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |

### PR Review

```bash
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

Or in a temporary clone:
```bash
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main'", pty=true)
```

---

## Common Pitfalls

1. **Always use `pty=true` for interactive TUI sessions** — agents like `codex` and `opencode` (TUI) hang without a PTY. One-shot `exec`/`run` commands do NOT need pty.
2. **Git repo required** — most agents won't run outside a git directory
3. **Use `--full-auto` or equivalent for building** — auto-approves changes within the sandbox
4. **Background for long tasks** — use `background=true` and monitor with `process` tool
5. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
6. **Parallel is fine** — run multiple agent processes at once for batch work in separate worktrees
7. **Path mismatch** — shell environments may resolve different binaries. Check with `which -a`
8. **Enter may need to be pressed twice** in TUI mode (once to finalize text, once to send)
9. **OpenCode: `/exit` is NOT a valid command** — use Ctrl+C