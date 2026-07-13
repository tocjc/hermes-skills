---
name: knowledge-vault-workflows
description: Build structured knowledge bases with wikilinks, generate headless graph visualizations, and manage vault-wide multi-note batches.
platforms: [linux, macos]
related_skills: [obsidian]
---

# Knowledge Vault Workflows

Use this skill alongside the bundled `obsidian` skill when the task involves:

- Creating a structured **multi-note knowledge base** (8+ notes) with cross-links
- Generating a **knowledge graph visualization** from `[[wikilinks]]` when Obsidian GUI is unavailable (headless/terminal)
- Designing a hub-and-spoke note architecture with README landing pages
- Embedding SVG/PNG graph renders into notes so the user can see the graph in Obsidian

---

## Headless Knowledge Graph Visualisation

When the user asks to "open the graph view" or "see the knowledge graph" and no display server is available (`$DISPLAY` unset):

### 1. Dependencies

```bash
apt-get install -y graphviz librsvg2-bin
pip install graphviz
```

### 2. Generate with `gen-knowledge-graph.py`

This skill ships a reusable script at `scripts/gen-knowledge-graph.py`.  
**It must be copied into the vault first**, then run:

```bash
# Copy script into vault, then run
python3 scripts/gen-knowledge-graph.py  # uses $OBSIDIAN_VAULT_PATH
# Or point to a specific vault
python3 scripts/gen-knowledge-graph.py --vault /path/to/vault
```

**What it does:**
- Scans all `.md` files in the vault
- Extracts every `[[wikilink]]` (stripping `#section` and `|display`)
- Builds a colour-coded directed graph with Graphviz (neato engine)
- Outputs `<vault>/assets/knowledge-graph.svg` (and `.png` if `rsvg-convert` available)
- Prints an `![[assets/knowledge-graph.svg]]` embed link

### 3. Embed in notes

Write the embed link into any note so the user sees the graph inside Obsidian:

```
![[assets/knowledge-graph.svg]]
```

Add to the README / hub page of the knowledge base, and the vault welcome note.

### 4. Colour convention

Extend `COLOR_MAP` in the script for new notes:

| Category | Colour | Hex |
|----------|--------|-----|
| Foundation / inputs | Blue | `#3182ce` |
| Analysis / diagnostics | Red | `#e53e3e` |
| Feature engineering / ML | Green | `#38a169` |
| Tools / references / tutorials | Purple | `#805ad5` / `#7c3aed` |
| Hub / index / meta | Gray | `#a0aec0` / `#718096` |

---

## Creating a Structured Knowledge Base

### Architecture guidelines

```
topic/
├── README.md          ← Hub page with overview, learning paths, data-flow
├── core-theory.md     ← Foundational note, referenced by all others
├── sub-a.md           ← Domain A, links back to core-theory
├── sub-b.md           ← Domain B
├── sub-c.md           ← Domain C with cross-links to A and B
├── tools.md           ← Tools, libraries, code snippets
└── cases.md           ← Real-world examples with template
```

### README hub checklist

- [ ] Tree or diagram of the knowledge area
- [ ] Learning-path recommendations (beginner / intermediate / advanced / applied)
- [ ] Data-flow or process-flow diagram (ASCII or Mermaid)
- [ ] Pre-requisite / dependency table for each note
- [ ] Embedded graph: `![[assets/knowledge-graph.svg]]`

### YAML frontmatter template

```yaml
---
created: {{date:YYYY-MM-DD}}
tags: [vibration, signal-processing, index]
aliases: [alias-1, alias-2]
---
```

### Linking strategy

| Goal | Syntax | Example |
|------|--------|---------|
| Cross-reference a section | `[[Note#Section]]` | `[[基础理论#采样定理]]` |
| Link to whole note | `[[Note Name]]` | `[[故障诊断]]` |
| Custom display text | `[[Note\|text]]` | `[[FFT 详解\|FFT]]` |
| Embed content inline | `![[Note]]` | `![[故障诊断#诊断流程]]` |
| Precise block anchor | `^block-id` | `^citation` |

### Pitfalls

- **Do NOT** put the hub page inside `.obsidian/` — it won't appear in the file explorer.
- Keep note names ≤ 20 chars for fast `[[` autocomplete.
- For orphan notes (few incoming links), add `related:` in frontmatter instead of forcing a link.
- Batch `write_file` calls for 8+ notes (parallel tool calls) — they're independent.
- After creating a knowledge base, **immediately generate and embed the graph** so the user sees the connection topology on first open.
- When using Japanese/Chinese note names, quote them in `[[ ]]` — Obsidian handles Unicode fine, but the graphviz script's `COLOR_MAP` needs explicit entries for each non-ASCII name.