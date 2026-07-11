# Kanban Worker — Full Pitfalls and Scenarios

## Tenant Isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant so context doesn't leak:
- Good: `business-a: Acme is our biggest customer`
- Bad (leaks): `Acme is our biggest customer`

## Heartbeats Worth Sending

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`, `"uploaded 47/120 videos"`
Bad: `"still working"`, empty notes, sub-second intervals. Every few minutes max.

## Claiming Cards You Created

Pass `created_cards` on `kanban_complete` with ids from successful `kanban_create` return values. The kernel verifies each id exists and was created by your profile — phantom ids block the completion.

```python
c1 = kanban_create(title="fix SQL injection", assignee="security-worker")
c2 = kanban_create(title="fix CSRF", assignee="web-worker")
kanban_complete(summary="Review done", created_cards=[c1["task_id"], c2["task_id"]])
```

## Review-Required Handoff

For code changes needing human review, block instead of complete:

```python
kanban_comment(body="review-required handoff:\n" + json.dumps({"changed_files": [...], "tests_passed": 14}))
kanban_block(reason="review-required: shipped rate limiter, needs eyes on key choice")
```

Use `kanban_complete` only for genuinely terminal tasks (one-line fixes, research writeups).

## Retry Diagnostics

- `timed_out` — previous attempt hit `max_runtime_seconds`. Chunk the work.
- `crashed` — OOM or segfault. Reduce memory footprint.
- `spawn_failed` — profile config issue. Block for human, don't retry blindly.
- `reclaimed` — task was archived; check status carefully.
- `blocked` — unblock comment should be in thread.

## Notification Routing

Configure in `~/.hermes/config.yaml`:
- `notification_sources: ['*']` — accept from all profiles
- `notification_sources: ['default', 'zilor-ppt']` — restrict to specific profiles

## Do NOT

- Call `delegate_task` as a substitute for `kanban_create`
- Call `clarify` as a worker — you're headless. Use `kanban_block` instead.
- Modify files outside `$HERMES_KANBAN_WORKSPACE`
- Create follow-up tasks assigned to yourself
- Complete a task you didn't actually finish

## Pitfalls

- **Task state can change between dispatch and startup** — always `kanban_show` first
- **Workspace may have stale artifacts** — check comment thread for context
- **Don't rely on CLI when tools are available** — `kanban_*` tools work across all backends
- **Review-required tasks should use block, not complete**
