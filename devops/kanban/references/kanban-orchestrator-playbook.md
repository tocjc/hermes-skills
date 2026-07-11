# Kanban Orchestrator — Full Detail

## Profile Discovery

Hermes setups vary widely. Before fanning out, ground decomposition in existing profiles:

```bash
hermes profile list
```

Or ask the user. Cache results for the conversation. Re-asking wastes turns.

## Decomposition Step-by-Step

### Step 1 — Understand the goal

Ask clarifying questions if ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Step 2 — Sketch the task graph

1. Extract lanes from the request
2. Map each lane to a discovered profile
3. Decide independence vs. gated
4. Create independent lanes as parallel cards with no parent links
5. Create synthesis/review cards with parent links

**Examples of prompts that should fan out:**
- "Build an app" → design card + engineering card + integration/review card
- "Fix blockers and check model variants" → fixer card + explorer card
- "Research docs and implement" → research card (parallel) + implementation card

Words like "also," "finally," "and" do NOT automatically imply dependency.

### Step 3 — Create tasks and link

```python
t1 = kanban_create(title="research: cost comparison", assignee="<profile-A>")["task_id"]
t2 = kanban_create(title="research: performance", assignee="<profile-A>")["task_id"]
t3 = kanban_create(title="synthesize recommendation", assignee="<profile-B>", parents=[t1, t2])["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`.

### Step 4 — Complete your own task

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes, 1 synthesis, 1 prose draft",
    metadata={"task_graph": {"T1": {"assignee": "profile-A", "parents": []}}},
)
```

### Step 5 — Report back

Tell the user what was created, naming actual profiles.

## Common Patterns

- **Fan-out + fan-in (research → synthesize):** N research cards, one synthesis with all as parents
- **Parallel implementation + validation:** implementer card + explorer card, reviewer card depends on both
- **Pipeline with gates:** planner → implementer → reviewer
- **Same-profile queue:** N tasks to same profile, serialized by dispatcher
- **Human-in-the-loop:** `kanban_block()` waits for input, dispatcher respawns after `/unblock`

## Goal-Mode Cards

For open-ended cards, pass `goal_mode=True`:
```python
kanban_create(title="Translate full docs to French", assignee="<profile>", goal_mode=True, goal_max_turns=15)
```

After each worker turn, an auxiliary judge evaluates against the card's title + body. Not done + budget remains → worker continues in-session.

## Recovering Stuck Workers

1. **Reclaim** (`hermes kanban reclaim <task_id>`) — abort running worker, reset to `ready`
2. **Reassign** (`hermes kanban reassign <task_id> <new-profile> --reclaim`)
3. **Change profile model** — edit profile config, then Reclaim

## Pitfalls

- **Inventing profile names** — dispatcher silently fails unknown assignees
- **Bundling independent lanes** — if user asks for two outcomes, create two cards
- **Over-linking** — "finally check X" may still be parallel
- **Forgetting dependency links** — use `parents`, not prose
- **Argument order for links** — `kanban_link(parent_id, child_id)` — parent first
- **Don't pre-create the whole graph if shape depends on intermediate findings**
