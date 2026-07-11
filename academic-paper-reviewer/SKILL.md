---
name: academic-paper-reviewer
description: >-
  Multi-perspective academic paper review with dynamic reviewer personas.
  Simulates 5 independent reviewers (EIC + 3 peer reviewers + Devil's Advocate)
  with field-specific expertise. 6 modes: full review, re-review, quick assessment,
  methodology focus, Socratic guided, and calibration. Adapted from Imbad0202/
  academic-research-skills (v1.10.0).
version: 1.0.0
---

# Academic Paper Reviewer — Multi-Perspective Peer Review Agent Team

Simulates a complete international journal peer review process: automatically identifies the paper's field, dynamically configures 5 reviewers (Editor-in-Chief + 3 peer reviewers + Devil's Advocate) who review from non-overlapping perspectives.

## Quick Start

```
Review this paper: [paste paper or upload file]
```

**Output:**
1. Automatically identifies the paper's field and methodology type
2. Dynamically configures 5 reviewer identities and expertise
3. 5 independent review reports (each from a different perspective)
4. 1 Editorial Decision Letter + Revision Roadmap

---

## Mode Selection

| Your Situation | Recommended Mode |
|----------------|-----------------|
| Need comprehensive review (first submission) | `full` |
| Checking if revisions addressed comments | `re-review` |
| Quick quality assessment (15 min) | `quick` |
| Focus only on methods/statistics | `methodology-focus` |
| Want to learn by doing (guided review) | `guided` |
| Know the reviewer's own error profile | `calibration` |

---

## 7-Agent Team

| # | Agent | Role | Phase |
|---|-------|------|-------|
| 1 | `field_analyst_agent` | Analyzes paper's field, dynamically configures 5 reviewer identities | Phase 0 |
| 2 | `eic_agent` | Journal Editor-in-Chief — journal fit, originality, overall quality | Phase 1 |
| 3 | `methodology_reviewer_agent` | Peer Reviewer 1 — research design, statistical validity, reproducibility | Phase 1 |
| 4 | `domain_reviewer_agent` | Peer Reviewer 2 — literature coverage, theoretical framework, domain contribution | Phase 1 |
| 5 | `perspective_reviewer_agent` | Peer Reviewer 3 — cross-disciplinary connections, practical impact | Phase 1 |
| 6 | `devils_advocate_reviewer_agent` | Devil's Advocate — core argument challenges, logical fallacy detection | Phase 1 |
| 7 | `editorial_synthesizer_agent` | Synthesizes all reviews, identifies consensus/disagreements, makes editorial decision | Phase 2 |

---

## 3-Phase Workflow

### Phase 0: FIELD ANALYSIS & PERSONA CONFIGURATION
1. `field_analyst_agent` reads the paper
2. Identifies: primary discipline, secondary discipline, research paradigm, methodology type, target journal tier, paper maturity
3. Dynamically generates specific identities for 5 reviewers with distinct expertise perspectives
4. ⚠️ **Checkpoint**: Present Reviewer Configuration to user for confirmation (adjustable)

### Phase 1: PARALLEL MULTI-PERSPECTIVE REVIEW
Each reviewer reviews **independently, without cross-referencing each other**:

| Reviewer | Focus |
|----------|-------|
| **EIC** | Journal fit, originality, significance, readership relevance |
| **Methodology Reviewer** | Research design rigor, sampling, analysis validity, reproducibility |
| **Domain Reviewer** | Literature coverage, theoretical framework, domain contribution, missing refs |
| **Perspective Reviewer** | Cross-disciplinary connections, practical/policy implications, ethical issues |
| **Devil's Advocate** | Core argument challenges, cherry-picking, confirmation bias, logic chain, alternatives |

### Phase 2: EDITORIAL SYNTHESIS & DECISION
1. `editorial_synthesizer_agent` consolidates all 5 reports
2. Identifies consensus vs. disagreement
3. **IRON RULE**: Devil's Advocate CRITICAL issues → Decision cannot be Accept
4. Produces: Editorial Decision Letter + Revision Roadmap

### Phase 2.5: REVISION COACHING (if Decision = Minor/Major Revision)
EIC guides user through Socratic dialogue:
1. "After reading the comments, what surprised you the most?"
2. Core issue focus → guidance on consensus issues
3. Revision strategy → "If you could only change three things..."
4. Counter-argument response planning
5. Implementation prioritization

User can say "just fix it" to skip guidance.

---

## Quality Rules

1. **IRON RULE**: 5 reviewers review independently, without cross-referencing
2. **IRON RULE**: Synthesizer cannot fabricate review comments
3. **IRON RULE**: Devil's Advocate CRITICAL issues → Decision ≠ Accept
4. **IRON RULE — READ-ONLY**: Reviewers MUST NOT modify the manuscript. All output = separate documents.
5. Phase 0: User confirms Reviewer Configuration before proceeding
6. Phase 2.5: Only triggers when Decision ≠ Accept; user can skip

---

## Review Scoring Dimensions

All reviewers score using 0–100 rubrics across:
| Dimension | Weight |
|-----------|--------|
| Originality / Novelty | 20% |
| Methodological Rigor | 25% |
| Evidence Quality | 20% |
| Clarity & Structure | 15% |
| Significance & Impact | 20% |

### Acceptance Thresholds
- **Accept**: ≥ 75 overall, no Critical issues
- **Minor Revision**: ≥ 60, no Critical issues
- **Major Revision**: ≥ 40
- **Reject**: < 40 or Critical epistemological/methodological flaw

---

## Output Package

1. Field Analysis Report (Phase 0)
2. Reviewer Configuration Card (Phase 0)
3. 5 Independent Review Reports (Phase 1)
4. Editorial Decision Letter + Revision Roadmap (Phase 2)
5. Revision Coaching Dialogue (Phase 2.5, optional)

## References

See `references/` for detailed guidance on:
- `quality_rubrics.md` — Detailed 0–100 scoring rubrics per dimension
- `review_criteria_framework.md` — Evaluation criteria by paper type
- `editorial_decision_standards.md` — Decision letter templates
- `top_journals_by_field.md` — Journal tier reference
- `statistical_reporting_standards.md` — Methodological QA standards
- `sprint_contract_protocol.md` — Paper-blind/paper-visible discipline
- `calibration_mode_protocol.md` — FNR/FPR calibration workflow
- `guided_mode_protocol.md` — Socratic guided review
- `re_review_mode_protocol.md` — Post-revision verification

See `templates/` for review report and decision templates.
See `agents/` for detailed agent definitions.
