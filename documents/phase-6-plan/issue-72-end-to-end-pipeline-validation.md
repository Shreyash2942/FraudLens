# Issue #72 Plan - Validate End-to-End Pipeline Execution

Issue: `#72`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Execute and verify the complete orchestration path (ingestion -> transformation -> validation) to confirm dependency correctness, stage outputs, and operational readiness.

## Task Breakdown

### 1) Execute end-to-end DAG run

Execution scope:

- run master DAG: `fraudlens_phase6_pipeline_orchestration`
- use controlled test batch with known dataset coverage
- run in local profile first, then CI-compatible profile validation path

Planned run modes:

- happy-path success run
- controlled failure run (validation gate fail)
- rerun/recovery path for transient task behavior

Required run context:

- `batch_id`
- `pipeline_run_id`
- `profile` and `target`
- strict mode flag

### 2) Confirm dependency order is correct

Dependency verification checks:

- ingestion tasks complete before transformation begins
- transformation layer gates enforce `bronze -> silver -> gold -> kpi`
- validation tasks execute only after transformation completion
- failed gate produces `upstream_failed` state for dependent tasks

Evidence expectations:

- Airflow graph view screenshots or task-state exports
- run timeline summary with ordered stage boundaries
- gate pass/fail indicators with timestamps

### 3) Validate outputs across stages

Stage output checks:

- ingestion outputs: dataset load status and batch summary artifact
- transformation outputs: dbt run artifact summaries by layer
- validation outputs: selector gate outcomes and readiness indicators
- final run artifact: consolidated status + metadata completeness

Cross-stage reconciliation:

- confirm expected row/selector count signals per stage
- confirm no missing artifact for any completed stage
- confirm blocking behavior prevented unsafe publish where applicable

### 4) Review logs and task outcomes

Log review checklist:

- each stage has structured start/end status logs
- failures include category, reason, and blocking gate metadata
- retry/timeout behavior matches policy configuration
- final logs expose artifact locations and run summary

Outcome review artifacts:

- end-to-end run summary JSON
- stage-specific evidence files
- failure scenario evidence and recovery notes
- final readiness report for issue closure

## Deliverables for Issue #72

- `documents/phase-6-validation-runbook.md` (execution and verification commands)
- `documents/validation/phase-6-e2e-run-artifacts.json`
- `documents/validation/phase-6-e2e-run-evidence.md`
- `documents/validation/phase-6-e2e-failure-recovery.md`
- `documents/phase-6-readiness-report.md`
- `documents/phase-6-plan/issue-72-end-to-end-pipeline-validation.md` (this plan)

## Commit Plan (Issue #72)

1. `chore(airflow-validation): add end-to-end execution runbook for issue 72`
2. `test(airflow-validation): execute full local pipeline and capture artifacts for issue 72`
3. `test(airflow-validation): validate retry and failure branch behavior for issue 72`
4. `docs(airflow-validation): publish phase 6 readiness report for issue 72`

## Acceptance Criteria Mapping

- end-to-end DAG executed: covered by execution scope and run modes
- dependency order confirmed: covered by dependency verification checks
- outputs validated across stages: covered by stage output checks and reconciliation
- logs/task outcomes reviewed: covered by log checklist and evidence artifacts

## Risk Notes

- local runtime resource constraints can create false negatives; capture infra-vs-logic failure category
- flaky transient failures can hide dependency issues; include controlled rerun evidence
- missing artifact consistency can weaken readiness confidence; enforce artifact completeness checks

## Open Decision Log

- confirm canonical test batch id for reproducible e2e validation
- confirm minimum number of successful consecutive runs before marking readiness
- confirm whether CI-triggered e2e run is required in this phase or next phase
