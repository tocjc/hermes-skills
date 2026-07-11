---
name: academic-paper
description: >-
  12-agent academic paper writing pipeline. 10 modes (full/plan/outline/revision/
  revision-coach/abstract/lit-review/format-convert/citation-check/disclosure).
  6 paper types, 5 citation formats, bilingual abstracts, LaTeX/DOCX/PDF output.
  Style Calibration + Writing Quality Check. Adapted from Imbad0202/
  academic-research-skills (v3.2.0).
version: 1.0.0
---

# Academic Paper — Paper Writing Agent Team

A 12-agent pipeline for writing publishable academic papers across all disciplines. Adapted for Hermes Agent from Imbad0202/academic-research-skills.

## Quick Start

```
Write a paper on [topic]
```

### Execution Flow
1. Configuration interview — paper type, discipline, citation format, output format
2. Literature search — systematic search strategy, source screening
3. Architecture design — paper structure, outline, word count
4. Argumentation — claim-evidence chains, logical flow
5. Full-text drafting — section-by-section, register adjustment
6. Citation compliance + bilingual abstract (parallel)
7. Peer review — five-dimension scoring + revision suggestions (max 2 rounds)
8. Output formatting — LaTeX/DOCX/PDF/Markdown

---

## Mode Selection

| Mode | Purpose | Output |
|------|---------|--------|
| `full` | Complete paper draft | Paper draft (IMRaD or domain-appropriate) |
| `plan` | Socratic guided planning | Chapter Plan + INSIGHT collection |
| `outline-only` | Detailed outline | Outline + evidence map |
| `revision` | Revise paper from reviewer feedback | Revised draft + R&R responses |
| `revision-coach` | Parse reviewer comments | Revision Roadmap + Response Letter Skeleton |
| `abstract-only` | Bilingual abstract | zh-TW + EN abstract + keywords |
| `lit-review` | Literature review section | Annotated bibliography in paper format |
| `format-convert` | Convert paper format | LaTeX/DOCX/PDF/MD output |
| `citation-check` | Verify citations | Citation error report |
| `disclosure` | AI usage disclosure | Venue-specific AI use statement |

**Default rule**: When ambiguous between `plan` and `full`, prefer `plan`.

---

## 12-Agent Team

| # | Agent | Phase |
|---|-------|-------|
| 1 | `intake_agent` | Phase 0 — Configuration interview; paper type, citation format, output format |
| 2 | `literature_strategist_agent` | Phase 1 — Search strategy, source screening, annotated bibliography |
| 3 | `structure_architect_agent` | Phase 2 — Paper structure, detailed outline, evidence map |
| 4 | `argument_builder_agent` | Phase 3 — Argument construction, claim-evidence chains, counter-argument handling |
| 5 | `draft_writer_agent` | Phase 4 — Section-by-section full draft writing |
| 6 | `citation_compliance_agent` | Phase 5a — Citation format verification, reference list, DOI checking |
| 7 | `abstract_bilingual_agent` | Phase 5b — Bilingual abstract zh-TW + EN |
| 8 | `peer_reviewer_agent` | Phase 6 — Simulated double-blind review, 5-dimension scoring |
| 9 | `formatter_agent` | Phase 7 — LaTeX/DOCX/PDF/MD output, citation format conversion |
| 10 | `socratic_mentor_agent` | Plan mode — Chapter-by-chapter Socratic guidance |
| 11 | `visualization_agent` | Phase 4/7 — Publication-quality figure code (Python/R) |
| 12 | `revision_coach_agent` | Revision-Coach mode — Parse review comments into structured roadmap |

---

## 8-Phase Workflow

```
Phase 0: CONFIG     -> [intake_agent]           -> Paper Configuration Record
Phase 1: RESEARCH   -> [literature_strategist]   -> Search Strategy + Source Corpus
Phase 2: ARCHITECT  -> [structure_architect]     -> Paper Outline + Evidence Map
Phase 3: ARGUMENT   -> [argument_builder]        -> Argument Blueprint
Phase 4: DRAFTING   -> [draft_writer]            -> Complete Draft
Phase 5a: CITATIONS -> [citation_compliance] ─┐  -> Citation Audit Report
Phase 5b: ABSTRACT  -> [abstract_bilingual]   ─┘  -> Bilingual Abstract  (parallel)
Phase 6: REVIEW     -> [peer_reviewer]           -> Review Report (max 2 loops)
Phase 7: FORMAT     -> [formatter]               -> Final Output Package
```

### Checkpoint Rules
1. **IRON RULE**: User must confirm Paper Configuration Record before Phase 1
2. Phase 2 → 3: User must approve outline
3. **IRON RULE**: Max 2 revision loops; unresolved → "Acknowledged Limitations"
4. Peer Review Critical-severity issues block Phase 7
5. User can skip Phase 1 (literature) if providing own sources

---

## Writing Quality Features

### Style Calibration (optional)
Provide 3+ past papers → the pipeline learns your writing voice (sentence rhythm, vocabulary, citation style). Applied as a soft guide; discipline conventions take priority.

### Writing Quality Check
Applied during draft self-review. Catches:
- AI-typical overused terms
- Em dash overuse
- Throat-clearing openers ("It is noteworthy that...")
- Uniform paragraph lengths
- Monotonous sentence rhythm

### Supported Output Formats
- **Text**: LaTeX (.tex + .bib), DOCX (via Pandoc), PDF, Markdown
- **Figures**: Python (matplotlib/seaborn) or R (ggplot2) with APA 7.0 formatting, colorblind-safe palettes
- **Citation Formats**: APA 7.0 (default), Chicago, MLA 9, IEEE, Vancouver

---

## Paper Types

| Type | Default Structure | Best For |
|------|------------------|----------|
| Research Article | IMRaD | Empirical studies |
| Case Study | Context-Method-Findings-Implications | Single case analysis |
| Literature Review | Thematic/Chronological | Field overview |
| Theoretical Paper | Proposition-Argument-Implications | New frameworks |
| Conference Paper | Problem-Approach-Results-Conclusion | Conference venues |
| Policy Brief | Executive Summary-Context-Options | Policy recommendations |

---

## References

See `references/` for detailed guidance on:
- `plan_mode_protocol.md` — Socratic planning workflow
- `writing_quality_check.md` — Anti-pattern checklist
- `paper_structure_patterns.md` — Template structures by paper type
- `citation_format_switcher.md` — Cross-format citation conversion
- `anti_leakage_protocol.md` — Data isolation patterns
- `vlm_figure_verification.md` — Figure integrity checks
- `statistical_visualization_standards.md` — Chart type decision trees
- `failure_paths.md` — Recovery from common failures

See `templates/` for paper templates by type.
See `agents/` for detailed agent definitions.
