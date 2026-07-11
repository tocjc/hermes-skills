---
name: kanban
description: Comprehensive Kanban multi-agent orchestration — orchestrator playbook, worker lifecycle, pitfalls, and external-codex lane integration.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, worker, collaboration, codex]
    related_skills: [hermes-agent, code-agents]
---

# Kanban Multi-Agent Orchestration

Kanban is Hermes' multi-agent work-queue system. It orchestrates work across profiles via a durable SQLite board. This umbrella covers three roles: **Orchestrator** (decomposition and routing), **Worker** (task execution lifecycle), and **Codex Lane** (using Codex CLI as an implementation lane from a worker).

## Section A: Orchestrator — Decomposition Playbook

The orchestrator decomposes goals into Kanban cards and routes them to the right profiles. Core lifecycle is auto-injected via `KANBAN_GUIDANCE`; this is the deeper playbook.

### Step 0: Discover Available Profiles Before Planning

Fan-out depends on what profiles actually exist. The dispatcher silently fails unknown assignees.

```bash
hermes profile list
```

### When to Use the Board (vs. Delegation)

Create Kanban tasks when:
1. Multiple specialists needed
2. Work should survive crash/restart
3. User may want to interject
4. Multiple subtasks can run in parallel
5. Review/iteration expected
6. Audit trail matters

### Anti-Temptation Rules

- **Do not execute the work yourself**
- **Split multi-lane requests** before creating cards
- **Run independent lanes in parallel**
- **Never create dependent work as independent ready cards** — use `parents=[...]`
- **If no specialist fits, ask the user**

### Decomposition Playbook

**Step 1** — Understand the goal
**Step 2** — Sketch the task graph: extract lanes, map to profiles, decide dependencies
**Step 3** — Create tasks with `kanban_create`, pass `parents=[...]` for dependencies
**Step 4** — Complete own task with `kanban_complete(summary=..., metadata=...)`
**Step 5** — Report back to user

### Goal-Mode Cards

For open-ended cards, pass `goal_mode=True` to wrap the worker in a Ralph-style goal loop. Write the body as explicit acceptance criteria.

See `references/kanban-orchestrator-playbook.md` for the full orchestrator detail (profile discovery, dependency graph examples, fan-out patterns, goal-mode details, and stuck-worker recovery).

## Section B: Worker — Pitfalls and Examples

The worker lifecycle (6 steps: orient → work → heartbeat → block/complete) is auto-injected. This covers deeper detail.

### Workspace Handling

| Kind | What it is | How to work |
|---|---|---|
| `scratch` | Fresh tmp dir | Read/write freely; GC'd on archive |
| `dir:<path>` | Shared persistent dir | Treat like long-lived state |
| `worktree` | Git worktree | Commit work here |

### Good Summary + Metadata Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14, "tests_passed": 14,
    },
)
```

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput",
    metadata={"recommendation": "vLLM", "benchmarks": {"vllm": 1.0, "sglang": 0.87}},
)
```

### Block Reasons That Get Answered Fast

Bad: `"stuck"`. Good: one sentence naming the specific decision needed.
```python
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth)?")
```

### Retry Scenarios

If `kanban_show` returns prior runs, don't repeat the same path:
- `timed_out` → chunk the work
- `crashed` → reduce memory footprint
- `spawn_failed` → profile config issue, block for human
- `reclaimed` → task was archived, check status
- `blocked` → unblock comment should be in thread

See `references/kanban-worker-pitfalls.md` for the full worker detail (heartbeat guidance, claiming cards you created, review-required handoff, notification routing, and Do Nots).

## Section C: Codex Lane — External Agent Integration

When a worker wants to use Codex CLI as an isolated implementation lane while keeping Hermes as the task lifecycle owner.

### When to Use

All of these must be true:
- Coding/refactor/migration task with clear acceptance criteria
- Bounded diff evaluable in one run
- Isolated git worktree available
- Hermes can run tests independently
- Prompt states all safety constraints

### Ownership Rules

1. **Hermes owns the lifecycle** — Codex never calls kanban tools
2. **Hermes owns final acceptance** — treat Codex commits as untrusted until reviewed
3. **Hermes owns test execution** — repeat verification independently
4. **Hermes owns safety** — reject if Codex changes safety boundaries
5. **Hermes owns cleanup** — kill stuck processes and remove worktrees

### Worktree and Branch Pattern

```bash
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
REPO="/path/to/repo"
SAFE_TASK="$(printf '%s' "$TASK_ID" | tr -cd '[:alnum:]_-')"
BRANCH="codex/${SAFE_TASK}/$(date -u +%Y%m%d%H%M%S)"
WORKTREE="/tmp/${SAFE_TASK}-codex-lane"

git -C "$REPO" fetch --all --prune
git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE"
```

### Mode Selection

Use `codex exec` for bounded one-shot edits:
```bash
terminal(command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
  workdir="$WORKTREE", background=True, pty=True, notify_on_complete=True)
```

Use Codex `/goal` only for broader multi-step work requiring durable objective tracking.

### Reconciliation Checklist

- [ ] `git status` shows only expected files
- [ ] Diff reviewed by Hermes
- [ ] No secrets or local artifacts included
- [ ] Safety constraints preserved
- [ ] Hermes ran canonical tests independently
- [ ] Accepted commits applied to Hermes-owned workspace

See `templates/pmb-codex-lane-prompt.md` for the full prompt template, and `references/kanban-codex-lane.md` for complete capability checks, kill behavior, and metadata schema.

## Common Pitfalls

- **Inventing profile names that don't exist** — dispatcher silently drops unknown assignees
- **Bundling independent lanes into one card** — create separate cards for independent outcomes
- **Over-linking because of wording** — "finally check X" may still be parallel if static
- **Forgetting dependency links** — use `parents=[...]` not prose
- **Calling `clarify` as a worker** — you're headless, use `kanban_block` instead
- **Treating Codex self-report as verification** — always inspect diff and rerun tests
- **Running Codex in dirty main checkout** — always isolate in worktree/branch