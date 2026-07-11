---
name: skill-acquisition
description: Acquire skills from external sources beyond the official hub — GitHub repos, direct SKILL.md URLs, custom taps, and batch installation workflows. Covers tap management, cross-referencing existing vs new skills, handling ecosystem skills with dependency chains (e.g. sn-* series), and verifying installation. Use when the user asks to "learn new skills", "install from a repo", "add a skills source", or when you need to acquire skills not in the official hub.
---

# Skill Acquisition — External Skills Installation

Hermes allows skills to come from sources beyond the built-in hub: GitHub repos, direct URLs, and custom taps. This skill covers the full workflow of discovering, installing, and verifying skills from these external sources.

## Workflow: Installing from an External GitHub Repo

### 1. Explore the Repo

First, understand the repo structure — is it a skills hub mirror, a custom collection, or a single skill?

```bash
# Check the bundled manifest (if it's a hub mirror/fork)
curl -sL --max-time 30 "https://raw.githubusercontent.com/<user>/<repo>/main/.bundled_manifest"

# Check the skills catalog
curl -sL --max-time 30 "https://raw.githubusercontent.com/<user>/<repo>/main/skills-catalog.md"

# List top-level directories
curl -sL "https://api.github.com/repos/<user>/<repo>/contents" \
  | python3 -c "import sys,json; [print(f\"{i['type']:8s} {i['name']}\") for i in json.load(sys.stdin)]"
```

**Key insight:** The bundled manifest lists all hub skill IDs and their hashes — this tells you at a glance whether the repo is a fork of the official hub, a custom collection, or both.

### 2. Add the Repo as a Tap

```bash
hermes skills tap add https://github.com/<user>/<repo>
hermes skills tap list   # verify
```

The tap makes the repo a known skill source, but **installing individual skills still requires explicit action**.

### 3. Cross-Reference with Existing Skills

Identify what's new:

```bash
# Your current inventory
find ~/.hermes/skills/ -name "SKILL.md" | sed 's|.*/skills/||' | sed 's|/SKILL.md||' | sort > /tmp/existing.txt

# Skills from the bundled manifest
curl -sL "https://raw.githubusercontent.com/<user>/<repo>/main/.bundled_manifest" \
  | cut -d: -f1 | sort > /tmp/remote.txt

# Skills NOT in your existing set
comm -23 /tmp/remote.txt /tmp/existing.txt
```

**Important:** The bundled manifest may list skills you already have — the hub version might differ. Prioritize downloading skills that are truly new (not in your inventory at all).

### 4. Install Individual Skills

**Option A — Hub install (tap must resolve correctly):**
```bash
hermes skills install <skill-id>
```

**Option B — Direct SKILL.md URL:**
```bash
hermes skills install "https://raw.githubusercontent.com/<user>/<repo>/main/<skill-dir>/SKILL.md" --name <skill-name>
```

**Option C — Batch manual download (preferred for 10+ skills):**
```bash
# Single skill
mkdir -p ~/.hermes/skills/<skill-name>
curl -sL --max-time 30 -o ~/.hermes/skills/<skill-name>/SKILL.md \
  "https://raw.githubusercontent.com/<user>/<repo>/main/<skill-dir>/SKILL.md"
```

For skills at the repo root (like sn-* skills), use the skill name directly as the directory.
For skills under categories (like `research/`, `finance/`), use `category/skill-name` as path.

### 5. Verify Installation

```bash
# Count total
find ~/.hermes/skills/ -name "SKILL.md" | wc -l

# List from Hermes registry
hermes skills list

# Check a specific skill loads
hermes skills inspect <skill-name>
```

**In-session:** use `/reload-skills` to pick up new skills without restarting.

## Tree-Based Discovery for Nested Sub-Skills

Some repos organize skills in deep nesting structures that aren't obvious from the top-level
directory listing. Example: `sn-da-excel-workflow` has 44 sub-skills under
`capability/{category}/{skill-name}/SKILL.md` — invisible from the root or even from `contents/`.

**Use the GitHub API recursive tree to uncover all SKILL.md files:**

```bash
# Get the full recursive tree (one shot, no pagination for small repos)
curl -sL --max-time 60 \
  "https://api.github.com/repos/<user>/<repo>/git/trees/main?recursive=1" \
  -o /tmp/repo-tree.json

# Extract all SKILL.md paths, group by parent skill name
python3 -c "
import json
from collections import defaultdict

with open('/tmp/repo-tree.json') as f:
    tree = json.load(f)['tree']

skills = defaultdict(list)
for item in tree:
    p = item['path']
    if p.endswith('SKILL.md') and item['type'] == 'blob':
        parts = p.split('/')
        skill_name = parts[-2]
        category = parts[-3] if len(parts) >= 3 else '(root)'
        skills[skill_name].append({'path': p, 'category': category})

for name, files in sorted(skills.items()):
    cats = set(f['category'] for f in files)
    print(f'{name:40s} ({", ".join(cats)})')
"
```

**Why this matters:** The recursive tree bypasses both GitHub's paginated contents API
(which hides subdirectories) and the need for git clone. It reveals:
- Skills nested under capability/domain/category directories
- Supporting files (references/, templates/, scripts/, agents/) within each skill
- Shared/protocol layers (like `academic-shared` with its `contracts/` directory)

## Batch Download for 10+ Skills

When installing many skills, individual `hermes skills install` calls are slow.
**Batch via curl + GitHub API tree:**

```bash
TREE_JSON=/tmp/repo-tree.json
BASE_URL="https://raw.githubusercontent.com/<user>/<repo>/main"

# For each new SKILL.md identified in the tree
python3 -c "
import json, os, subprocess

with open('$TREE_JSON') as f:
    tree = json.load(f)['tree']

existing = set(os.listdir(os.path.expanduser('~/.hermes/skills/')))

for item in tree:
    p = item['path']
    if not p.endswith('SKILL.md') or item['type'] != 'blob':
        continue
    parts = p.split('/')
    skill_name = parts[-2]
    if skill_name in existing:
        continue  # skip already-installed
    
    target = os.path.expanduser(f'~/.hermes/skills/{skill_name}/SKILL.md')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    url = f'$BASE_URL/{p}'
    subprocess.run(['curl', '-sL', '--max-time', '30', '-o', target, url])
    if os.path.getsize(target) > 20:
        print(f'  ✅ {skill_name}')
    else:
        os.remove(target)
        print(f'  ❌ {skill_name}')
"
```

**Pro tip:** For repos with supporting files (references/, templates/, scripts/), extend
the script to download those too — filter by skill_name in the path and download every blob.

Some skills form ecosystems with dependency chains. For example, the `sn-*` series:

```
sn-deep-research        → sn-research-planning, sn-dimension-research,
                          sn-research-synthesis, sn-research-report,
                          sn-report-format-discovery, sn-search-*

sn-ppt-entry            → sn-ppt-creative OR sn-ppt-standard
sn-ppt-creative/standard → sn-image-base, sn-ppt-doctor

sn-da-excel-workflow    → sn-da-large-file-analysis, sn-da-image-caption
```

**Always install the full dependency chain.** Check each SKILL.md's references and
the skills-catalog for the relationship map. Missing a dependency will cause the
orchestrator skill to fail mid-workflow.

## Common Pitfalls

### 🔴 Tap path mismatch
`hermes skills tap add` may imply a `skills/` subdirectory in the repo, but skills
might be at the repo root. The tap is a registration hint, not a physical path.
Always verify the actual repo structure before assuming paths.

### 🔴 raw.githubusercontent.com timeouts
GitHub's raw CDN can be slow (especially from China/Asia). Mitigations:
- Use `--max-time 30` or higher with curl
- Retry on failure — the first attempt may fail while the second succeeds
- Use the GitHub API for lightweight directory listings instead

### 🔴 git clone fails (proxy/TLS issues)

Common scenarios in restricted networks: proxy redirects (`insteadOf` git config pointing
to a Chinese mirror), GnuTLS errors, connection timeouts.

**Fallback strategy — GitHub API + curl:**

```bash
# 1. Get the full recursive tree
curl -sL --max-time 60 \
  "https://api.github.com/repos/<user>/<repo>/git/trees/main?recursive=1" \
  -o /tmp/repo-tree.json

# 2. Parse to find all SKILL.md paths
python3 -c "
import json
with open('/tmp/repo-tree.json') as f:
    tree = json.load(f)['tree']
for item in tree:
    if item['path'].endswith('SKILL.md') and item['type'] == 'blob':
        parts = item['path'].split('/')
        skill_name = parts[-2]
        print(f'{item[\"path\"]}  →  {skill_name}')
"

# 3. Download each SKILL.md via raw.githubusercontent.com
curl -sL --max-time 30 -o ~/.hermes/skills/<skill-name>/SKILL.md \
  "https://raw.githubusercontent.com/<user>/<repo>/main/<path-to>/SKILL.md"
```

**Key insight:** `raw.githubusercontent.com` often works even when `github.com` (with proxy)
fails because it's a different CDN endpoint not routed through the proxy.

### 🔴 14-byte "404: Not Found" responses
A successful curl with exactly 14 bytes is GitHub's `404: Not Found` page.
Check the URL path: does the SKILL.md exist at that path? Is it at repo root
or under a category directory?

### 🔴 GitHub API rate limiting
The REST API has a 60 req/hour limit per IP for unauthenticated requests.
Use `raw.githubusercontent.com` for actual file downloads, not the API.
When API-limited, fall back to curl + raw URLs entirely.

### 🔴 Skills not showing after install
- Run `hermes skills list` (not just `ls` the directory)
- In-session: use `/reload-skills` 
- Skills take effect in new sessions or after `/reset` — they don't auto-load
  into the current conversation unless explicitly loaded via `/skill <name>`

### 🔴 Overlapping skills from multiple sources
When a skill exists both in the official hub and a custom repo, the hub
version wins if installed via `hermes skills install`. Manually copying
SKILL.md to `~/.hermes/skills/` overwrites the hub version.

## External Source Reference

| Source | Install Method | Auto-Update | Verification |
|--------|---------------|-------------|--------------|
| Official hub | `hermes skills install <id>` | `hermes skills update` | `hermes skills check` |
| GitHub tap | `hermes skills tap add` + install | Manual re-install | `hermes skills inspect` |
| Direct URL | `hermes skills install <url>` | Manual re-install | Inline during install |
| Manual copy | curl + `~/.hermes/skills/` | None | `hermes skills list` |

## Supporting Files

This skill ships with the following reference documents:

| File | Content |
|------|---------|
| `references/tocjc-hermes-skills-ecosystem.md` | Full dependency map and usage guide for the tocjc/hermes-skills repo ecosystem (SN deep research, PPT, Excel, search skills) |

## Skill Structure Convention

Skills are stored at `~/.hermes/skills/<category>/<skill-name>/SKILL.md`.
Skills without a category go directly at `~/.hermes/skills/<skill-name>/SKILL.md`.

Supporting files:
- `references/` — session-specific detail, error transcripts, domain notes
- `templates/` — starter files meant to be copied and modified
- `scripts/` — statically re-runnable actions
