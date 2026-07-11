---
name: dogfood
description: "Exploratory QA of web apps: find bugs, evidence, reports."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, testing, browser, web, dogfood, self-improvement, learnings]
    related_skills: []
---

# Dogfood: Systematic Web Application QA Testing

## Overview

This skill guides you through systematic exploratory QA testing of web applications using the browser toolset. You will navigate the application, interact with elements, capture evidence of issues, and produce a structured bug report.

## Prerequisites

- Browser toolset must be available (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_vision`, `browser_console`, `browser_scroll`, `browser_back`, `browser_press`)
- A target URL and testing scope from the user

## Inputs

The user provides:
1. **Target URL** — the entry point for testing
2. **Scope** — what areas/features to focus on (or "full site" for comprehensive testing)
3. **Output directory** (optional) — where to save screenshots and the report (default: `./dogfood-output`)

## Workflow

Follow this 5-phase systematic workflow:

### Phase 1: Plan

1. Create the output directory structure:
   ```
   {output_dir}/
   ├── screenshots/       # Evidence screenshots
   └── report.md          # Final report (generated in Phase 5)
   ```
2. Identify the testing scope based on user input.
3. Build a rough sitemap by planning which pages and features to test:
   - Landing/home page
   - Navigation links (header, footer, sidebar)
   - Key user flows (sign up, login, search, checkout, etc.)
   - Forms and interactive elements
   - Edge cases (empty states, error pages, 404s)

### Phase 2: Explore

For each page or feature in your plan:

1. **Navigate** to the page:
   ```
   browser_navigate(url="https://example.com/page")
   ```

2. **Take a snapshot** to understand the DOM structure:
   ```
   browser_snapshot()
   ```

3. **Check the console** for JavaScript errors:
   ```
   browser_console(clear=true)
   ```
   Do this after every navigation and after every significant interaction. Silent JS errors are high-value findings.

4. **Take an annotated screenshot** to visually assess the page and identify interactive elements:
   ```
   browser_vision(question="Describe the page layout, identify any visual issues, broken elements, or accessibility concerns", annotate=true)
   ```
   The `annotate=true` flag overlays numbered `[N]` labels on interactive elements. Each `[N]` maps to ref `@eN` for subsequent browser commands.

5. **Test interactive elements** systematically:
   - Click buttons and links: `browser_click(ref="@eN")`
   - Fill forms: `browser_type(ref="@eN", text="test input")`
   - Test keyboard navigation: `browser_press(key="Tab")`, `browser_press(key="Enter")`
   - Scroll through content: `browser_scroll(direction="down")`
   - Test form validation with invalid inputs
   - Test empty submissions

6. **After each interaction**, check for:
   - Console errors: `browser_console()`
   - Visual changes: `browser_vision(question="What changed after the interaction?")`
   - Expected vs actual behavior

### Phase 3: Collect Evidence

For every issue found:

1. **Take a screenshot** showing the issue:
   ```
   browser_vision(question="Capture and describe the issue visible on this page", annotate=false)
   ```
   Save the `screenshot_path` from the response — you will reference it in the report.

2. **Record the details**:
   - URL where the issue occurs
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Console errors (if any)
   - Screenshot path

3. **Classify the issue** using the issue taxonomy (see `references/issue-taxonomy.md`):
   - Severity: Critical / High / Medium / Low
   - Category: Functional / Visual / Accessibility / Console / UX / Content

### Phase 4: Categorize

1. Review all collected issues.
2. De-duplicate — merge issues that are the same bug manifesting in different places.
3. Assign final severity and category to each issue.
4. Sort by severity (Critical first, then High, Medium, Low).
5. Count issues by severity and category for the executive summary.

### Phase 5: Report

Generate the final report using the template at `templates/dogfood-report-template.md`.

The report must include:
1. **Executive summary** with total issue count, breakdown by severity, and testing scope
2. **Per-issue sections** with:
   - Issue number and title
   - Severity and category badges
   - URL where observed
   - Description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshot references (use `MEDIA:<screenshot_path>` for inline images)
   - Console errors if relevant
3. **Summary table** of all issues
4. **Testing notes** — what was tested, what was not, any blockers

Save the report to `{output_dir}/report.md`.

## Tools Reference

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to a URL |
| `browser_snapshot` | Get DOM text snapshot (accessibility tree) |
| `browser_click` | Click an element by ref (`@eN`) or text |
| `browser_type` | Type into an input field |
| `browser_scroll` | Scroll up/down on the page |
| `browser_back` | Go back in browser history |
| `browser_press` | Press a keyboard key |
| `browser_vision` | Screenshot + AI analysis; use `annotate=true` for element labels |
| `browser_console` | Get JS console output and errors |

## Tips

- **Always check `browser_console()` after navigating and after significant interactions.** Silent JS errors are among the most valuable findings.
- **Use `annotate=true` with `browser_vision`** when you need to reason about interactive element positions or when the snapshot refs are unclear.
- **Test with both valid and invalid inputs** — form validation bugs are common.
- **Scroll through long pages** — content below the fold may have rendering issues.
- **Test navigation flows** — click through multi-step processes end-to-end.
- **Check responsive behavior** by noting any layout issues visible in screenshots.
- **Don't forget edge cases**: empty states, very long text, special characters, rapid clicking.
- When reporting screenshots to the user, include `MEDIA:<screenshot_path>` so they can see the evidence inline.

---

## Post-QA: Self-Improvement Through Learnings Capture

After completing a QA session, capture lessons learned to improve future testing. Use this structured approach to log errors, corrections, and best practices discovered during QA.

### When to Log

| Scenario | What to Log |
|----------|-------------|
| A test failed in an unexpected way | Error + root cause to `ERRORS.md` |
| The user corrected your approach | Correction to `LEARNINGS.md` |
| You found a better testing pattern | Best practice to `LEARNINGS.md` |
| The user requested a missing QA capability | Feature request to `FEATURE_REQUESTS.md` |
| A bug pattern keeps recurring across sessions | Promote to a Hermes skill |

### Dual-Track Recording

Hermes has two permanent stores for durable knowledge — use the right one:

| What | Where | When |
|------|-------|------|
| User preferences, environment facts, tool quirks | `memory` tool | Immediately, single fact per entry |
| Reusable workflows, vetted patterns, QA procedures | `skill_manage` | After 3+ occurrences across tasks |
| Session-specific bug details, one-shot errors, feature requests | `.learnings/` files (project-local) | Immediately after discovery |

### .learnings/ File Format

Initialize in the project root:

```bash
mkdir -p .learnings
for f in LEARNINGS.md ERRORS.md FEATURE_REQUESTS.md; do
  [ -f ".learnings/$f" ] || touch ".learnings/$f"
done
```

**LEARNINGS.md** — corrections, insights, best practices:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Priority**: low | medium | high | critical
**Area**: frontend | backend | infra | tests | docs | config

### Summary
What was learned in one sentence

### Details
Full context: what happened, what was wrong, what's right

### Suggested Action
How to apply this learning
```

**ERRORS.md** — command failures and integration errors:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Priority**: high
**Area**: frontend | backend | infra | tests | docs | config

### Summary
What failed

### Error
```
actual error output
```

### Context
What was attempted, inputs, environment

### Suggested Fix
How to fix next time
```

### Promotion to Skill

When a learning proves widely applicable (3+ occurrences, 2+ different tasks, within 30 days):

1. Extract the pattern into a reusable procedure
2. Save as a skill with `skill_manage(action='create', ...)`
3. Update the `.learnings/` entry status to `promoted` and note the skill name

### Key Principle

Log immediately after the event — context is freshest right after a QA session ends. A delayed log is as good as no log.
