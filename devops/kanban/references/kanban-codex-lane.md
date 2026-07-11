# Kanban Codex Lane — Full Detail

## Codex Capability Checks

Run these before spawning Codex:
```bash
command -v codex
codex --version
codex features list | grep -i goals || true
```

If `/goal` support required:
```bash
codex features enable goals || true
codex --enable goals --version
```

Auth can be via `OPENAI_API_KEY` or Codex CLI OAuth state (`~/.codex/auth.json`). A missing `OPENAI_API_KEY` is not proof auth is unavailable.

## Prompt Construction

Every Codex prompt must include:
- `task_id`, title, and full Kanban acceptance criteria
- Repo path, worktree path, branch name, and allowed file scope
- Explicit statement: Hermes owns Kanban lifecycle; Codex is an input lane only
- Required output: concise summary, files changed, commits, tests run, known risks
- Prohibited actions: secrets access, external messaging, board mutation, unrelated refactors

For prediction-market-bot (PMB), include these safety constraints verbatim:
```text
- live-SIM is paper-only; do not add or enable live REST order entry.
- Never use market orders.
- Do not add execution crossing or bypass price/risk checks.
- Do not fake passive fills, fills, PnL, order states, or reconciliation evidence.
- Do not weaken risk gates, limits, kill switches, or fail-closed behavior.
- Keep research/selection outside the C++ hot path unless explicitly requested.
- Do not read, print, write, or require secrets/tokens/credentials.
```

## Monitoring, Timeout, and Kill Behavior

```python
result = terminal(command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE, background=True, pty=True, notify_on_complete=True)
session_id = result["session_id"]

# Monitor
process(action="poll", session_id=session_id)
process(action="log", session_id=session_id, limit=200)
process(action="wait", session_id=session_id, timeout=300)

# Send Kanban heartbeat
kanban_heartbeat(note="Codex lane running in <WORKTREE>; waiting for tests/diff")
```

Kill conditions:
- No useful output for remaining runtime budget
- Codex requests secrets or production credentials
- Codex modifies files outside worktree
- Codex starts unrelated rewrites

```python
process(action="kill", session_id=session_id)
```

## Reconciliation Checklist

- [ ] `git status` shows only expected files
- [ ] Diff reviewed by Hermes — no secrets, credentials, unrelated data
- [ ] PMB safety constraints preserved
- [ ] Codex commits are small enough to cherry-pick
- [ ] Hermes ran canonical tests independently
- [ ] Accepted commits applied to Hermes-owned workspace

## Acceptance Outcomes

- `accepted`: Codex diff reviewed, applied, and verified
- `partial`: Some work accepted after edits; rejected parts documented
- `rejected`: No changes accepted
- `timed_out`: Codex exceeded budget

## Metadata Schema

Include under `kanban_complete.metadata.codex_lane`:
```json
{
  "codex_lane": {
    "used": true,
    "mode": "exec | goal | skipped",
    "worktree": "/path/to/worktree",
    "branch": "codex/t_caa69668/20260508100000",
    "result": "accepted | rejected | partial | timed_out",
    "accepted_commits": ["<sha1>"],
    "rejected_reason": "concrete reason",
    "tests_run": [{"command": "scripts/run_tests.sh", "exit_code": 0, "owner": "hermes"}]
  }
}
```
