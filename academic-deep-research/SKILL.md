---
name: academic-deep-research
description: >-
  Universal deep research agent team for rigorous academic research on any topic.
  7 modes: full, quick brief, review, lit-review, fact-check, Socratic guided,
  and systematic review (PRISMA 2020). Covers RQ formulation → methodology design
  → systematic literature search → source verification → cross-source synthesis →
  risk of bias assessment → meta-analysis → APA 7.0 report → editorial review.
  Adapted from Imbad0202/academic-research-skills (v2.9.4).
version: 1.0.0
---

# Academic Deep Research — Universal Research Agent Team

A domain-agnostic 13-agent research pipeline for rigorous academic investigation. Adapted for Hermes Agent from Imbad0202/academic-research-skills `deep-research` skill.

## Quick Start

```
Research the impact of [topic]
```

**Socratic mode** (when you need guidance):
```
Guide my research on [topic]
```

### Execution Flow
1. **Scoping** — Research question + methodology blueprint
2. **Investigation** — Systematic literature search + source verification
3. **Analysis** — Cross-source synthesis + bias check
4. **Composition** — Full APA 7.0 report
5. **Review** — Editorial + ethics + vulnerability scan
6. **Revision** — Final polished report

---

## Mode Selection Guide

| Your Situation | Recommended Mode |
|----------------|-----------------|
| Vague idea, need guidance | `socratic` |
| Clear RQ, need comprehensive research | `full` |
| Need a quick brief (30 min) | `quick` |
| Have a paper to evaluate before citing | `review` |
| Need literature review on a topic | `lit-review` |
| Need to verify specific claims | `fact-check` |
| Need systematic review / meta-analysis | `systematic-review` |

**Default rule**: When ambiguous between `socratic` and `full`, **prefer `socratic`**.

### Socratic Mode Activation

Activate when user:
1. Has no clear RQ and wants guided thinking
2. Asks to be "led", "guided", or "mentored" through research
3. Expresses uncertainty about where to start
4. Wants to brainstorm or clarify a research direction
5. Describes a vague interest without a specific question

---

## 6-Phase Workflow

### Phase 1: SCOPING (Interactive)
1. **Research Question Agent** → RQ Brief w/ FINER criteria scoring + scope boundaries + 2-3 sub-questions
2. **Research Architect Agent** → Methodology Blueprint (paradigm, method, data strategy, analytical framework)
3. **Devil's Advocate Agent** → CHECKPOINT: RQ clarity, method fit, scope width → PASS/REVISE verdict
4. ⟐ **User confirmation** before proceeding

### Phase 2: INVESTIGATION
1. **Bibliography Agent** → Systematic search strategy + Source Corpus + Annotated Bibliography (APA 7.0)
   - Database selection, keyword strategy, Boolean operators
   - Inclusion/exclusion criteria
   - PRISMA-style flow diagram
2. **Source Verification Agent** → Evidence hierarchy grading (Level I-VII), predatory journal screening, COI flagging, source quality matrix

### Phase 3: ANALYSIS
1. **Synthesis Agent** → Thematic synthesis, contradiction resolution, gap analysis, evidence convergence/divergence map
2. **Devil's Advocate Agent** → CHECKPOINT: cherry-picking, confirmation bias, logic chain, alternative explanations

### Phase 4: COMPOSITION
1. **Report Compiler Agent** → APA 7.0 report draft: Title → Abstract → Intro → Method → Findings → Discussion → References
2. Apply **Writing Quality Check** — flag AI-typical overused terms, sentence/paragraph length variation, throat-clearing openers

### Phase 5: REVIEW
1. **Editor-in-Chief Agent** → Originality, rigor, evidence sufficiency → Verdict (Accept/Revise/Reject)
2. **Devil's Advocate Agent** → Assumption challenges, logical fallacy detection, alternative explanations
3. **Ethics Review Agent** → AI research ethics, attribution, dual-use screening

### Phase 6: REVISION
1. Incorporate editorial feedback into final report
2. **Monitoring Agent** (optional) → Post-research literature monitoring setup

---

## Systematic Review Mode (PRISMA 2020)

Additional agents activated for `systematic-review` mode:
- **Risk of Bias Agent** → RoB 2 (RCTs) / ROBINS-I (non-randomized) with traffic-light visualization
- **Meta-Analysis Agent** → Effect sizes, heterogeneity (I²), GRADE assessment

Follow PRISMA 2020 27-item checklist; use `references/systematic_review_protocol.md` for detailed guidance.

---

## Quality Gates

1. **Checkpoint 1** (end of Phase 1): Devil's Advocate must PASS before Phase 2
2. **Checkpoint 2** (end of Phase 3): Devil's Advocate must PASS before Phase 4
3. **Source Verification**: Every source graded on evidence hierarchy; predatory journals flagged
4. **Writing Quality**: AI-typical patterns checked before final delivery
5. **Final QA**: All citations verified, logic chains validated, alternatives explored

## Output Format

- **Markdown report** (default) — APA 7.0 structure
- Title, Abstract, Introduction, Method, Findings, Discussion, References
- Annotated bibliography appended
- Source quality matrix included

## References

See `references/` for detailed guidance on:
- `socratic_mode_protocol.md` — Socratic questioning framework
- `systematic_review_protocol.md` — PRISMA 2020 full workflow
- `source_quality_hierarchy.md` — Evidence level I-VII grading
- `methodology_patterns.md` — Research paradigm selection
- `apa7_style_guide.md` — APA 7.0 formatting rules
- `mode_selection_guide.md` — Detailed mode decision tree
- `logical_fallacies.md` — Devil's Advocate reference
- `ethics_checklist.md` — Research ethics review
- `failure_paths.md` — Common failure modes and recovery
