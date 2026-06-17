# Issue #73 Plan - Document Orchestration Design & Operations

Issue: `#73`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Produce complete orchestration documentation covering DAG design, dependencies, scheduling/retry behavior, and operator usage for ongoing implementation and maintenance.

## Task Breakdown

### 1) Document DAG structure

Documentation targets:

- master DAG architecture and purpose
- supporting DAG roles (ingestion, transformation, validation)
- task-group model and stage boundaries
- shared runtime/config helpers and profile usage

Planned artifacts:

- Phase 6 architecture reference doc with DAG topology diagrams/tables
- per-DAG summary sections with inputs, outputs, and key parameters

### 2) Document task dependencies

Dependency documentation scope:

- stage order: ingestion -> transformation -> validation
- layer order in transformation: bronze -> silver -> gold -> kpi
- validation checkpoints and downstream blocking behavior
- gate semantics for critical vs warning outcomes

Planned outputs:

- dependency matrix table (task group to task group)
- failure propagation map (`failed`, `upstream_failed`, retry paths)
- sample run sequence timeline for happy and failure paths

### 3) Document scheduling and retry behavior

Operational behavior documentation:

- schedule modes (`manual`, `daily`, `ci_triggered`)
- default retry and timeout policy by task class
- strict-mode and fail-fast behavior
- policy overrides by profile/environment

Runbook content:

- how to trigger manual runs
- how to pass runtime params (`batch_id`, profile, selector overrides)
- how to interpret retries/timeouts in Airflow UI

### 4) Update README and operations notes

Planned docs updates:

- update `airflow/README.md` with Phase 6 DAG set and usage
- update `airflow/dags/README.md` with DAG-level intent and constraints
- add/refresh operations notes for troubleshooting and recovery
- update `documents/README.md` to include final phase 6 documentation set

Operational notes scope:

- local sync flow (`scripts/sync_airflow_dags_to_fraudlens_container.ps1`)
- import error checks and DAG parsing tips
- common failure diagnostics and remediation paths

## Deliverables for Issue #73

- `documents/phase-6-orchestration-design-reference.md`
- `documents/phase-6-orchestration-operations-runbook.md`
- `documents/phase-6-orchestration-dependency-matrix.md`
- `airflow/README.md` (Phase 6 update)
- `airflow/dags/README.md` (Phase 6 update)
- `documents/orchestration-airflow.md` (final phase summary refresh)
- `documents/phase-6-plan/issue-73-orchestration-design-operations-docs.md` (this plan)

## Commit Plan (Issue #73)

1. `docs(airflow): publish phase 6 orchestration design reference for issue 73`
2. `docs(airflow): publish operator runbook and troubleshooting guide for issue 73`
3. `docs(airflow): publish CI/CD integration and handoff checklist for issue 73`
4. `docs(airflow): publish final phase 6 summary artifact for issue 73`

## Acceptance Criteria Mapping

- DAG structure documented: covered by architecture reference and per-DAG sections
- task dependencies documented: covered by dependency matrix and failure propagation map
- scheduling/retry behavior documented: covered by runtime policy and runbook sections
- README/ops notes updated: covered by airflow/docs index and operations notes refresh

## Risk Notes

- documentation drift from implementation can reduce operational trust; update docs in same PRs as DAG changes
- missing dependency/failure examples can create ambiguity during incidents; include explicit failure-path examples
- mixed local/ci behavior without clear profile notes can cause misconfiguration; keep profile tables explicit

## Open Decision Log

- confirm final naming of Phase 6 final consolidated document
- confirm whether CI/CD handoff checklist is included here or split to Phase 8 preparation notes
- confirm minimum operations evidence required before issue closure
