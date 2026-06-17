# Issue #69 Plan - Integrate Validation & Quality Checks

Issue: `#69`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Embed validation and quality controls directly in orchestration so unsafe data is blocked before downstream stages execute.

## Task Breakdown

### 1) Add dbt test tasks

Planned validation task groups:

- `validate_preflight`
- `validate_bronze_gate`
- `validate_silver_gate`
- `validate_gold_gate`
- `validate_kpi_gate`
- `validate_governance_gate`
- `validate_publish_artifacts`

Planned dbt validation commands:

- `dbt test --select tag:bronze`
- `dbt test --select tag:silver`
- `dbt test --select tag:gold`
- `dbt test --select tag:kpi`
- critical selectors:
  - `dbt test --select quality_critical_gate`
  - `dbt test --select governance_critical_gate`
  - `dbt test --select contract_critical_gate`
  - `dbt test --select audit_traceability_gate`

### 2) Place validation in correct dependency order

Validation order contract:

1. Bronze build complete -> Bronze validation gate
2. Silver build complete -> Silver validation gate
3. Gold build complete -> Gold validation gate
4. KPI build complete -> KPI validation gate
5. Governance/contract/audit gates -> final readiness gate

Orchestration dependency policy:

- validation tasks are stage-coupled and cannot be skipped in strict mode
- each downstream transformation stage is blocked until prior stage validation passes
- final publish task runs only after all critical gates pass

### 3) Define validation checkpoints between layers

Checkpoint model:

- `checkpoint_bronze_to_silver`
- `checkpoint_silver_to_gold`
- `checkpoint_gold_to_kpi`
- `checkpoint_kpi_to_publish`

Checkpoint behavior:

- each checkpoint validates required selector counts and pass/fail status
- checkpoints log decision metadata (`pass`, `block`, `warn`) with reason codes
- checkpoint outputs are written to run artifacts for audit/review

### 4) Confirm failed validation stops dependent work

Failure handling policy:

- critical validation failure: immediate block of dependent tasks
- non-critical warning tests: recorded but allowed only where policy permits
- deterministic validation failures: no automatic retries
- transient execution failures: bounded retries with timeout guardrails

Expected blocked-flow evidence:

- task graph shows downstream tasks as `upstream_failed` when gates fail
- run artifact includes failure gate name and blocking selector
- issue evidence includes failed test snippet and blocked dependency snapshot

## Deliverables for Issue #69

- `airflow/dags/fraudlens_phase6_validation_workflow.py`
- `airflow/dags/fraudlens_phase6_pipeline_orchestration.py` (validation gate wiring)
- `airflow/dags/_fraudlens_phase6_common.py` (dbt test command wrappers + policy helpers)
- `airflow/tests/test_phase6_validation_dag.py`
- `documents/phase-6-plan/issue-69-validation-quality-integration.md` (this plan)

## Commit Plan (Issue #69)

1. `feat(airflow-validation): scaffold phase 6 validation dag for issue 69`
2. `feat(airflow-validation): add critical quality and governance gate tasks for issue 69`
3. `feat(airflow-validation): integrate contract and failure-policy validators for issue 69`
4. `feat(airflow-validation): add validation evidence publish step for issue 69`
5. `test(airflow-validation): add validation dag import and blocking-path tests for issue 69`

## Acceptance Criteria Mapping

- dbt test tasks added: covered by stage and selector validation task groups
- validation placed in correct order: covered by stage-coupled dependency contract
- checkpoints defined between layers: covered by checkpoint model and behavior
- failed validation stops dependent work: covered by blocking policy and evidence expectations

## Risk Notes

- over-broad selectors may increase runtime and hide critical-path intent; maintain explicit gate selector sets
- inconsistent test severity mapping can allow unsafe progression; align with Phase 5 failure policy matrix
- retries on deterministic test failures can waste runtime and obscure root cause; restrict retry classes

## Open Decision Log

- confirm strict/default mode for local developer runs vs CI runs
- confirm whether KPI gate is mandatory in every run or optional via selector profile
- confirm artifact storage location convention for validation outputs (`documents/validation/` vs airflow artifacts path)
