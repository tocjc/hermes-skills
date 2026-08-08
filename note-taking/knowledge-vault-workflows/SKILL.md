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

---

## Import External Documents (docx/pdf → Vault)

When a user asks to "add a document to 知识库" — convert external `.docx`/`.pdf`/`.txt` files into structured Obsidian notes.

### Workflow

1. **Read source** — `read_file` auto-extracts `.docx`/`.pdf` to text.
2. **Convert to Markdown** — YAML frontmatter (`tags`, `source:` path) + structured body. Convert tables to Markdown tables, sections to headings, lists to bullet lists.
3. **Place in correct vault subdirectory**:

| Document type | Directory | Example |
|--------------|-----------|---------|
| Project quotation / bid / proposal | `projects/` | `projects/项目报价.md` |
| Technical reference / spec / standard | `references/` | `references/某标准.md` |
| Domain-specific knowledge | Topic subdirectory | `topic/某领域.md` |

4. **Write to vault** — `write_file(path=f"{OBSIDIAN_VAULT_PATH}/subdir/名称.md", content=...)`.
5. **Add vector memory** — `memory_vec(action='add', content='1-3 sentence summary', tags=['tag1', 'tag2'])` for semantic recall across sessions.

### Pitfalls

- **Do NOT** leave `.docx`/`.pdf` in the vault — convert to `.md` first.
- Vector memory entry should be concise (1-3 sentences), not a full-text dump.
- If `OBSIDIAN_VAULT_PATH` is unset, fallback to `~/notes/obsidian-vault/` (the user's known vault path).
- For tabular data (budgets, specs), Markdown tables are far more legible than raw text blocks.

---

## Import External Files from Disk

When the user provides a file path (e.g. `/root/李渔全集研究报告.md`) and asks to add it to the knowledge base — this is a distinct pattern from docx/pdf conversion or user-typed text.

### Workflow

1. **Read the file** — `read_file(path)` to inspect content and structure.
2. **Add YAML frontmatter** — prepend `tags`, `created:`, `source:` original path to make it a proper Obsidian note.
3. **Write to vault** — `write_file(path=f"{OBSIDIAN_VAULT_PATH}/subdir/名称.md", content=...)`.
4. **Cross-link to related notes** — Search for existing notes on the same topic, `patch` each to append a `[[wikilink]]` back to the new note.
5. **Index to vector memory** — `memory_vec(action='add', content='concise 1-3 sentence summary with unique contribution', tags=[...])`.

### Copy vs Write

For files already in Markdown format, either `cp` (terminal) or `write_file` works:
- `write_file` is preferred when adding frontmatter or restructuring the body.
- `cp` + `patch` for frontmatter is faster for large, well-structured files where only metadata needs adding.

### Pitfalls

- **Always add frontmatter** — a raw `.md` file without `tags:` and `created:` is invisible to Obsidian's search and graph.
- **Source path** — record `source: /root/原始文件.md` in frontmatter; do NOT delete the source file without user consent (the `rm` command may be blocked).
- **Vector memory** — index every file added; semantic recall is the only way to find it later if the user doesn't remember the filename.

---

## Knowledge Chain: Multiple Notes on the Same Topic

When the user adds several files on the **same topic** across multiple turns (e.g. 5 Li Yu research notes), create a **cross-linked knowledge chain**.

### Pattern

Each new note:
1. Links **back** to all previous notes on the same topic in its "关联笔记" section
2. Gets a **backlink** appended to the most comprehensive existing note
3. Has a **unique contribution summary** (e.g. "本篇特色：...") to distinguish its value from siblings

### Consolidation

After 3+ notes on the same topic accumulate, the chain becomes a knowledge cluster. Each note's "关联笔记" section should list all siblings with a one-line summary of each one's unique contribution:

```
[[li-yu-research-guide|李渔研究]] — 5大研究价值与5个核心热点
[[李渔全集研究报告]] — 22卷册文献构成、7条选题方向、7类研究方法
[[李渔全集研究_硕士生视角]] — 版本谱系、研究热点量化分布图、语言学选题方向
```

### Example (from session)

```
Li Yu notes chain (5 notes, 4 user turns):
  li-yu-research-guide.md                ← 5 values + 5 hotspots
  → 李渔全集研究报告.md                   ← 22 vols + 7 directions
  → 李渔全集研究_硕士生视角.md             ← version lineage + linguistics
  → 《李渔全集》研究价值与学术前沿.md        ← 10 scholars + 5 methodologies
  → 李渔全集研究_硕士生深入挖掘.md         ← market-literature crossover + 20 topics
```

Each link is bidirectional; each note's "关联笔记" section lists all siblings.

---

## Curate User-Provided Text into Vault

When the user directly provides text content (not from a file) and asks to save it to the knowledge base — this is a distinct pattern from docx/pdf import.

### Workflow

1. **Format as structured note** — Add YAML frontmatter with `tags`, `created` date, and relevant aliases. Structure the body with headings, tables, and code blocks.
2. **Place in correct vault subdirectory** — follow the same table as "Import External Documents" above.
3. **Write to vault** — `write_file(path=f"{OBSIDIAN_VAULT_PATH}/subdir/名称.md", content=...)`.
4. **Cross-link to related existing notes** — Search for existing notes on related topics, then `patch` each to append a `[[wikilink]]` back to the new note. Creates bidirectional links.
5. **Index to vector memory** — `memory_vec(action='add', content='concise summary', tags=[...])` for semantic recall.

### Example session pattern

```
User: "把下列内容加入知识库：[long text about Topic A]"
→ write_file  → save as references/topic-a.md
→ patch       → add [[topic-a]] link to existing references/related-topic.md
→ memory_vec  → index for semantic search
```

### Pitfalls

- **Cross-linking is not optional** — a note without `[[wikilinks]]` is an orphan. Always search for related notes and add backlinks.
- For sequences (e.g. Topic A → Topic A vs B comparison → Topic A selection guide), create a **knowledge chain**: each new note links back to the previous one, and the first note gets an update to link forward.
- Anchor `patch` on the existing "关联笔记" section or the end of the file. If no section exists, add one and link back.
- Batch independent writes and patches (parallel) when creating 3+ notes.
- Use consistent tag taxonomy: `[深度学习, 损失函数, 类别不平衡]` for technical topics, `[项目, 报价, 投标]` for business docs.
- **Do NOT** put the hub page inside `.obsidian/` — it won't appear in the file explorer.
- Keep note names ≤ 20 chars for fast `[[` autocomplete.
- For orphan notes (few incoming links), add `related:` in frontmatter instead of forcing a link.
- After creating a knowledge base, **immediately generate and embed the graph** so the user sees the connection topology on first open.
- When using Japanese/Chinese note names, quote them in `[[ ]]` — Obsidian handles Unicode fine, but the graphviz script's `COLOR_MAP` needs explicit entries for each non-ASCII name.