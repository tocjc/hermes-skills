---
name: academic-pipeline
description: >-
  Orchestrator for the full academic research pipeline: research → write →
  integrity check → review → revise → re-review → revise → final integrity →
  finalize. Coordinates academic-deep-research, academic-paper, and
  academic-paper-reviewer into a seamless 10-stage workflow with mandatory
  integrity verification and two-stage peer review. Adapted from Imbad0202/
  academic-research-skills (v3.10.0).
version: 1.0.0
---

# Academic Pipeline — Full Research Workflow Orchestrator

A lightweight orchestrator that manages the complete academic pipeline from research exploration to final manuscript. It does not perform substantive work — it detects stages, recommends modes, dispatches skills, manages transitions, and tracks state.

## Quick Start

**Full workflow (from scratch):**
```
I want to write a research paper on [topic]
```
→ Pipeline launches from Stage 1 (RESEARCH)

**Mid-entry (existing paper):**
```
I already have a paper, help me review it
```
→ Pipeline starts from Stage 2.5 (INTEGRITY)

**Revision mode (received reviewer feedback):**
```
I received reviewer comments, help me revise
```
→ Pipeline starts from Stage 4 (REVISE)

---

## Pipeline Stages (10 Stages)

| Stage | Name | Skill Used | Deliverables |
|-------|------|-----------|-------------|
| 1 | RESEARCH | `academic-deep-research` | RQ Brief, Methodology, Bibliography, Synthesis |
| 2 | WRITE | `academic-paper` (plan/full) | Paper Draft |
| **2.5** | **INTEGRITY** | **Integrity Verification** | Integrity report + corrected paper |
| 3 | REVIEW | `academic-paper-reviewer` (full) | 5 review reports + Editorial Decision + Roadmap |
| 4 | REVISE | `academic-paper` (revision) | Revised Draft + Response to Reviewers |
| **3'** | **RE-REVIEW** | `academic-paper-reviewer` (re-review) | Verification checklist + residual issues |
| **4'** | **RE-REVISE** | `academic-paper` (revision) | Second revised draft (if needed) |
| **4.5** | **FINAL INTEGRITY** | **Integrity Verification** | Final verification (must be 100%) |
| 5 | FINALIZE | `academic-paper` (format-convert) | Final Paper (MD/DOCX/LaTeX/PDF) |
| 6 | PROCESS SUMMARY | Orchestrator | Creation process record |

---

## State Machine

```
Stage 1 (RESEARCH) → user confirm → Stage 2
Stage 2 (WRITE) → user confirm → Stage 2.5
Stage 2.5 (INTEGRITY) → PASS → Stage 3 | FAIL → fix (max 3 rounds)
Stage 3 (REVIEW) → Accept → Stage 4.5 | Minor/Major → Stage 4 | Reject → revise or end
Stage 4 (REVISE) → user confirm → Stage 3'
Stage 3' (RE-REVIEW) → Accept/Minor → Stage 4.5 | Major → Stage 4'
Stage 4' (RE-REVISE) → user confirm → Stage 4.5 (no return to review)
Stage 4.5 (FINAL INTEGRITY) → PASS (zero issues) → Stage 5
Stage 5 (FINALIZE) → MD → DOCX → LaTeX → PDF → Stage 6
Stage 6 (PROCESS SUMMARY) → Generate process record → end
```

---

## Adaptive Checkpoint System

**IRON RULE**: After each stage completion, proactively prompt user and wait for confirmation.

### Checkpoint Types

| Type | When Used | Content |
|------|-----------|---------|
| FULL | First checkpoint; after integrity boundaries; before finalization | Full deliverables + dashboard + all options |
| SLIM | After 2+ consecutive "continue" responses on non-critical stages | One-line status + continue/pause prompt |
| MANDATORY | Integrity FAIL; Review decision; Stage 5 | Cannot be skipped |

### Self-Check Questions (at every FULL checkpoint)
Before presenting to user, ask:
1. **Citation integrity**: Are there unverified citations?
2. **Sycophantic concession**: Did last stage accept all feedback uncritically?
3. **Quality trajectory**: Is latest output ≥ previous stage quality?
4. **Scope discipline**: Did last stage add unrequested content?

---

## Integrity Verification (Stages 2.5 & 4.5)

Run by `integrity_verification_agent`:

1. **Reference Verification**: Each citation → confirm paper exists, claims match source
2. **Data Integrity**: Numbers match across text/tables/figures? Statistical values consistent?
3. **Plagiarism Scan**: Check for unreferenced overlap with existing work
4. **Logic Chain**: Argument flow is sound, no gaps
5. **Format Compliance**: Journal guidelines followed

**Pass criteria**: 100% of references verified, zero unresolved integrity flags

### Integrity Recovery (Stage 2.5 → Stage 3)
- Critical (blocker): Fix required before proceeding
- Major (fix-and-continue): Fix flagged issues, continue
- Minor (log-and-continue): Log acknowledgment, continue

---

## Quality Gates Summary

1. ✅ Stage 2.5 INTEGRITY → 100% pass required for pipeline
2. ✅ Stage 3 REVIEW → Critical issues block Accept decision
3. ✅ Stage 3' RE-REVIEW → Verification that all changes addressed
4. ✅ Stage 4.5 FINAL INTEGRITY → Zero issues required
5. ✅ Stage 5 FINALIZE → Output format validation

### Parallelization (v3.3+)
Within Stage 2 (academic-paper), after outline completes:
- `literature_strategist_agent` and `visualization_agent` can run in parallel
- `draft_writer_agent` waits for both to complete

---

## Mid-Entry Detection Rules

| User Statement | Detected Entry Point |
|----------------|---------------------|
| "I want to research [topic]" | Stage 1 |
| "I have results/outline, help me write" | Stage 2 |
| "I have a draft, check its integrity" | Stage 2.5 |
| "I have a draft, review it" | Stage 3 |
| "I have review comments, help me revise" | Stage 4 |
| "I have a revised draft, re-review" | Stage 3' |
| "Finalize my paper" | Stage 5 |

---

## References

See `references/` for detailed guidance on:
- `pipeline_state_machine.md` — Complete state transition definitions
- `integrity_review_protocol.md` — Integrity check procedures
- `claim_verification_protocol.md` — Claim-level verification
- `two_stage_review_protocol.md` — Review/re-review flow
- `plagiarism_detection_protocol.md` — Plagiarism checks
- `mode_advisor.md` — Stage-specific mode recommendations
- `passport_as_reset_boundary.md` — Cross-session resume via Material Passport
- `process_summary_protocol.md` — Paper creation process doc
- `progress_dashboard_template.md` — Status dashboard template
- `score_trajectory_protocol.md` — Quality score tracking
- `reinforcement_content.md` — Mid-conversation reinforcement content
- `external_review_protocol.md` — Third-party reviewer integration
- `team_collaboration_protocol.md` — Multi-agent handoff rules
- `ai_research_failure_modes.md` — Failure mode reference (Lu et al. 2026)

See `agents/` for detailed agent definitions.
