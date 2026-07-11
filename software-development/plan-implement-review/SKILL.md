---
name: plan-implement-review
description: Complete software development pipeline — write implementation plans, execute via subagents with two-stage review, and run pre-commit verification gates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [planning, implementation, subagent, code-review, verification, tdd]
    related_skills: [test-driven-development, systematic-debugging, spike, codebase-inspection]
---

# Plan → Implement → Review Pipeline

A complete software development workflow covering three phases: **write a plan**, **execute via subagents with two-stage review**, and **run pre-commit verification**. Each phase feeds into the next.

## Core Pipeline

```
Requirements → [Phase 1: Plan] → [Phase 2: Implement via Subagents] → [Phase 3: Review & Verify] → Commit
```

---

## Phase 1: Writing Implementation Plans

Write comprehensive plans with bite-sized tasks (2-5 min each). Assume the implementer has zero codebase context.

### Plan Structure

Every plan starts with:
```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence]

**Architecture:** [2-3 sentences]

**Tech Stack:** [Key technologies]

---
```

### Task Structure (Bite-Sized)

Each task = one focused action:
```markdown
### Task N: [Descriptive Name]

**Objective:** What this accomplishes

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`

**Step 1: Write failing test**
```python
def test_behavior():
    assert function(input) == expected
```

**Step 2: Run test to verify failure**
Run: `pytest tests/path/test.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**
```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**
Expected: PASS

**Step 5: Commit**
```
```

### Writing Process

1. Understand requirements
2. Explore the codebase
3. Design approach
4. Write tasks (setup → core → edge cases → integration → cleanup)
5. Add complete details (exact paths, complete code, exact commands, verification)
6. Review the plan

### Principles

- **DRY** — extract shared logic
- **YAGNI** — only what's needed now
- **TDD** — failing test before code
- **Frequent commits** — after every task

See `references/writing-plans.md` for full detail.

---

## Phase 2: Subagent-Driven Development

Execute plans by dispatching fresh subagents per task with two-stage review.

### Per-Task Workflow

**Step 1: Dispatch Implementer Subagent**
```python
delegate_task(
    goal="Implement Task 1: Create User model",
    context="""TASK FROM PLAN:
    - Create: src/models/user.py
    - User class with email (str) and password_hash (str) fields
    
    FOLLOW TDD:
    1. Write failing test
    2. Verify it fails
    3. Write minimal implementation
    4. Verify it passes
    
    PROJECT CONTEXT:
    - Python 3.11, Flask app
    - Tests use pytest
    """,
    toolsets=['terminal', 'file']
)
```

**Step 2: Dispatch Spec Compliance Reviewer**
```python
delegate_task(
    goal="Review if implementation matches the spec",
    context="""CHECK:
    - [ ] All requirements implemented?
    - [ ] File paths match spec?
    - [ ] Nothing extra added?
    
    OUTPUT: PASS or list of specific gaps.""",
    toolsets=['file']
)
```

**Step 3: Dispatch Code Quality Reviewer**
```python
delegate_task(
    goal="Review code quality",
    context="""CHECK:
    - [ ] Project conventions followed?
    - [ ] Proper error handling?
    - [ ] Clear naming?
    - [ ] Adequate test coverage?
    
    OUTPUT: Critical Issues / Important / Minor / APPROVED""",
    toolsets=['file']
)
```

**Step 4: Mark complete** and proceed to next task.

### Efficiency Notes

- **Fresh subagent per task** — prevents context pollution
- **Two-stage review** — spec compliance first, then code quality
- **Handle issues** — if reviewer finds issues, fix → re-review; don't skip

See `references/subagent-driven-development.md` for full detail, including references on context budget discipline and the four gate types.

---

## Phase 3: Pre-Commit Verification

Automated verification pipeline before code lands. Security scan, baseline-aware quality gates, independent reviewer subagent, and auto-fix loop.

### Step 1 — Get the diff
```bash
git diff --cached
```
If empty, try `git diff` then `git diff HEAD~1 HEAD`.

### Step 2 — Static security scan
```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token)\s*=\s*['\"][^'\"]{6,}['\"]"

# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"

# SQL injection
git diff --cached | grep "^+" | grep -E "execute\(f\"|\.format\(.*SELECT"
```

### Step 3 — Baseline tests and linting
Detect project and run tools. Capture baseline (stash changes, run, pop). Only NEW failures block commit.

```bash
python -m pytest --tb=no -q 2>&1 | tail -5
which ruff && ruff check . 2>&1 | tail -10
```

### Step 4 — Self-review checklist
- [ ] No hardcoded secrets
- [ ] Input validation on user data
- [ ] SQL queries use parameterized statements
- [ ] No debug print/console.log left behind
- [ ] New code has tests

### Step 5 — Independent reviewer subagent

```python
delegate_task(
    goal="Independent code review. Return ONLY valid JSON.",
    context="""FAIL-CLOSED: security concerns or logic errors => passed=false.
    
    {static scan results}
    
    {git diff}
    
    Return: {"passed": bool, "security_concerns": [], "logic_errors": [], "suggestions": [], "summary": "verdict"}"""
)
```

### Step 6 — Auto-fix loop (max 2 cycles)

Spawn a fix subagent for reported issues, then re-verify.

### Step 7 — Commit
```bash
git add -A && git commit -m "[verified] <description>"
```

See `references/pre-commit-verification.md` for full detail.

---

## Integration with Other Skills

- **test-driven-development** — enforce RED-GREEN-REFACTOR in every implementation step
- **systematic-debugging** — use when bugs are found during implementation
- **spike** — validate feasibility before writing full plans
- **codebase-inspection** — understand project structure before planning

## Common Pitfalls

1. **Skipping the plan** — implementation without a plan leads to context pollution
2. **Skipping reviews** — spec compliance AND quality review are both required
3. **Tasks too big** — keep 2-5 min each; if task takes longer, split it
4. **Starting quality review before spec compliance passes** — wrong order
5. **Empty diff at verification time** — check `git status` first
6. **Large diff (>15k chars)** — split by file, review each separately
7. **Subagent reads the plan file** — provide full task text in context instead
8. **Auto-fix introduces new issues** — counts as a new failure, cycle continues