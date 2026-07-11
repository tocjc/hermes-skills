---
name: academic-shared
description: >-
  Shared protocols, schemas, and reference materials shared across all
  ARS-derived academic skills (academic-deep-research, academic-paper,
  academic-paper-reviewer, academic-pipeline). Contains style calibration,
  mode spectrum, cross-model verification, compliance protocols, and
  ground truth isolation patterns. Adapted from Imbad0202/
  academic-research-skills shared/ directory.
version: 1.0.0
---

# Academic Shared — Cross-Skill Protocols & Schemas

Shared protocols used by all ARS-derived academic skills. Load this skill when you need protocol-level reference material for quality control, style calibration, or compliance checks during an academic writing/research workflow.

## Protocols

### Style Calibration Protocol
Learn the user's writing voice from 3+ past papers. Applied as a soft guide during drafting:
- Sentence rhythm analysis
- Vocabulary preference mapping
- Citation integration style extraction
- Discipline conventions always take priority

### Mode Spectrum Framework
All skills use a three-tier spectrum for output style:
| Spectrum | Style | Best For |
|----------|-------|----------|
| `fidelity` | Template-heavy, predictable output | Mechanical tasks, format conversion |
| `balanced` | Default — structured but flexible | Full research, writing, review |
| `originality` | Exploratory, template-light | Guided/Socratic modes, brainstorming |

### Cross-Model Verification (opt-in)
Set `ARS_CROSS_MODEL=1` to verify key outputs with a second model:
- Literature search results validated by alternate model
- Reference verification cross-checked
- Review scores independently verified
- Report compiler claims validated

### Compliance Checkpoint Protocol
RAISE framework for AI-assisted research compliance:
- **R**eproducibility — Can methods be replicated from the description?
- **A**ttribution — Are contributions properly credited?
- **I**ntegrity — Are data and analysis free from fabrication?
- **S**ource verification — Are references real and accurate?
- **E**thics — Are ethical guidelines followed?

### Ground Truth Isolation Pattern
Data access levels for pipeline stages:
| Level | Description | Used By |
|-------|-------------|---------|
| `raw` | Full access to all data and instructions | deep-research |
| `redacted` | Metadata only, no raw data | academic-paper |
| `verified_only` | Only verified, cross-checked data | reviewer, pipeline |

### Sprint Contract Protocol (v3.6.2+)
Paper-blind → paper-visible call discipline for generator-evaluator separation:
- Phase 4a: Writer pre-commits to acceptance criteria before seeing the paper
- Phase 4b: Writer drafts with full paper context
- Phase 6a: Evaluator pre-commits scoring plan before seeing the draft
- Phase 6b: Evaluator scores with full draft context

### Benchmark Report Schema
JSON Schema for honest, verifiable benchmark comparisons in publications.

### Artifact Reproducibility Pattern
Optional `repro_lock` for Material Passport artifacts. Configuration documentation only — LLM outputs are not byte-reproducible.

### Collaboration Depth Rubric
| Depth | Description |
|-------|-------------|
| L1 | Mechanical execution (format conversion) |
| L2 | Supervised generation (drafting with review) |
| L3 | Collaborative reasoning (Socratic dialogue) |
| L4 | Delegated judgment (user trusts agent decisions) |

## Files

### Shared References
- `references/firm_rules.md` — Cross-skill IRON RULE definitions
- `references/intent_clarification_protocol.md` — Cross-skill routing rules
- `references/protected_hedging_phrases.md` — Academic hedging conventions
- `references/word_count_conventions.md` — Word count standards across fields

### Shared Agents
- `agents/compliance_agent.md` — RAISE compliance verification agent

### Schemas (in `contracts/`)
- Writer contracts: `contracts/writer/full.json`
- Evaluator contracts: `contracts/evaluator/full.json`
- Reviewer contracts: `contracts/reviewer/full.json`, `contracts/reviewer/methodology_focus.json`
- Passport schemas: citation provenance, claim audit, constraint violations, rejection logs, timeline
- Audit schemas: verdict, JSONL, sidecar

### Policy Data
- `policy_data/nature_policy.md` — Nature journal AI policy reference

### Templates
- `templates/codex_audit_multifile_template.md` — Audit template

## Usage

Load this skill alongside any academic-* skill when you need:
- `shared/style_calibration_protocol.md` — To calibrate writing voice
- `shared/mode_spectrum.md` — To understand fidelity/balanced/originality spectrum
- `shared/cross_model_verification.md` — To enable multi-model verification
- `shared/sprint_contract.schema.json` — For generator-evaluator contract

## Relationship to Other Skills

| Skill | Loads academic-shared for |
|-------|--------------------------|
| academic-deep-research | Mode spectrum, style profile consumption, writing quality check |
| academic-paper | Style calibration, writing quality check, sprint contracts |
| academic-paper-reviewer | Mode spectrum, sprint contract protocol, compliance |
| academic-pipeline | Material passport schemas, compliance checkpoints |