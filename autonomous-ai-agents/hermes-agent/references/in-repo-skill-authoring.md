# Authoring In-Repo (Bundled) Skills for Hermes Agent

This reference covers writing SKILL.md files that ship *with* the hermes-agent package (under `skills/<category>/<name>/SKILL.md` in the repo tree), not user-local skills (`~/.hermes/skills/`).

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- Use `write_file` + `git add` — `skill_manage(action='create')` writes to `~/.hermes/skills/`

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`.

- Starts with `---` as the first bytes (no leading blank line)
- Closes with `\n---\n` before the body
- `name` field present (≤64 chars, lowercase+hyphens)
- `description` field present, ≤1024 chars
- Non-empty body after the closing `---`

```yaml
---
name: my-skill-name
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill]
---
```

## Size Limits

- Description: ≤1024 chars
- Full SKILL.md: ≤100,000 chars (~36k tokens)
- Peer skills sit at 8-14k chars. Past 20k, split into `references/*.md`

## Directory Placement

```
skills/<category>/<name>/SKILL.md
```

Existing categories: `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

## Workflow

1. Survey peers in the target category
2. Draft with `write_file` to `skills/<category>/<name>/SKILL.md`
3. Validate locally (YAML frontmatter, name/description present, size limits)
4. `git add` + `git commit`
5. Note: current session won't see the new skill until a fresh session

## Pitfalls

1. **Using `skill_manage(action='create')` for in-repo skills** — writes to `~/.hermes/skills/`, not the repo tree
2. **Leading whitespace before `---`** — starts-with check fails
3. **Description too generic** — start with "Use when ..."
4. **Forgetting the author/license/metadata block** — every peer has it
5. **Expecting current session to see the new skill** — won't until next session
6. **Linking to skills that don't exist in-repo** — `related_skills` resolves at load time; prefer in-repo references