# Writing Implementation Plans — Full Detail

## Principles Reference

### DRY (Don't Repeat Yourself)
**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)
**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

### TDD (Test-Driven Development)
Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

### Frequent Commits
Commit after every task: `git add [files] && git commit -m "type: description"`

## Common Mistakes

### Vague Tasks
**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code
**Bad:** "Step 1: Add validation function"
**Good:** Complete function code included

### Missing Verification
**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths
**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Plan Mode Execution

When the user invokes `/plan` or says "make a plan first", switch to plan-only mode:
- Do not implement code
- Do not edit project files except the plan markdown file
- Do not run mutating terminal commands
- Deliverable is a markdown plan saved under `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

## Remember
```text
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```
