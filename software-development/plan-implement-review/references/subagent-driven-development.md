# Subagent-Driven Development — Full Detail

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context
- Ignore subagent questions
- Accept "close enough" on spec compliance
- Start code quality review before spec compliance is PASS
- Move to next task while either review has open issues

## Handling Issues

- **Subagent asks questions** — answer clearly and completely
- **Reviewer finds issues** — implementer fixes, reviewer reviews again
- **Subagent fails a task** — dispatch a new fix subagent with specific instructions

## Integration with Other Skills

- **writing-plans** — this skill EXECUTES plans created by writing-plans
- **test-driven-development** — implementer subagents should follow TDD
- **requesting-code-review** — two-stage review IS the code review
- **systematic-debugging** — if subagent encounters bugs, follow systematic debugging

## References

- `references/context-budget-discipline.md` — Four-tier context degradation model and read-depth rules
- `references/gates-taxonomy.md` — The four canonical gate types for validation checkpoints
