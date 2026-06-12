# FraudLens Documents

This directory contains the canonical written documentation for the project.

## Phase Consolidation Map

Use these as the primary phase review and handoff files:

| Phase | Primary File | Notes |
|---|---|---|
| `0` | `phase-0-readiness.md` | standards-first repo readiness checklist |
| `1` | `platform-foundation.md` | consolidated platform/runtime integration and validation handoff |
| `2` | `synthetic-data-foundation.md` | consolidated synthetic data design and delivery handoff |
| `3` | `warehouse-layer-foundation.md` | consolidated warehouse setup, runbook, and readiness handoff |
| `4` | `transformation-layer-dbt.md` | consolidated dbt transformation layer handoff |
| `5` | `data-quality-governance.md` | consolidated quality, governance, readiness, and controls handoff |
| `6` | `orchestration-airflow.md` | consolidated Airflow orchestration branch handoff |

Future phases `7` through `10` do not yet have their final consolidated handoff documents in `documents/`.

## Canonical Documents

- `project-charter.md` business context, objectives, and guiding decisions
- `implementation-roadmap.md` phase-by-phase delivery model
- `architecture-overview.md` platform and domain architecture summary
- `governance-overview.md` governance principles, control model, and audit posture
- `github-project-management.md` milestones, label taxonomy, and workflow conventions
- `phase-0-readiness.md` checklist for the standards-first baseline
- `platform-foundation.md` consolidated Phase 1 platform integration and validation document
- `platform-foundation-guide.md` Phase 1 runtime integration guide
- `platform-validation-runbook.md` Phase 1 validation and connectivity checks
- `synthetic-data-foundation.md` consolidated Phase 2 synthetic data design and delivery document
- `warehouse-layer-foundation.md` consolidated Phase 3 warehouse planning, runbooks, and readiness document
- `transformation-layer-dbt.md` consolidated Phase 4 dbt transformation planning, governance, and readiness document
- `graphify-workflow.md` Graphify usage and branch portability workflow
- `data-quality-governance.md` consolidated Phase 5 document (issues `#57`-`#64`, controls, validation, readiness, and handoff)
- `orchestration-airflow.md` consolidated Phase 6 branch handoff for `orchestration-airflow`, including architecture, operations, MongoDB artifact persistence, validation status, and commit ledger

## Supporting Airflow Reference Set

These remain available as detailed supporting references behind `orchestration-airflow.md`:

- `airflow-orchestration-design-reference.md`
- `airflow-orchestration-dependency-matrix.md`
- `airflow-orchestration-operations-runbook.md`
- `airflow-orchestration-cicd-handoff-checklist.md`
- `airflow-e2e-validation-runbook.md`
- `airflow-orchestration-readiness-report.md`
- `airflow-observability-lineage-design.md`
- `airflow-observability-operations-runbook.md`

## Planning Workspace

- `phase-6-plan/` detailed per-sub-issue planning workspace for Phase 6 implementation

Legacy `.docx` files are retained as reference sources only. Active planning and design content should be maintained in Markdown and YAML.
