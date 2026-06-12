# Issue #70 Plan - Configure Scheduling, Retries & Failure Handling

Issue: `#70`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Configure operational orchestration controls so pipeline runs are resilient, repeatable, and governance-aligned across normal, retry, and failure paths.

## Task Breakdown

### 1) Define schedule strategy

Schedule modes:

- `manual` (default for local developer control)
- `daily` (production-like recurring window)
- `ci_triggered` (on-demand validation orchestration)

Planned schedule policy:

- master pipeline DAG defaults to `schedule=None` in local mode
- environment profile can promote to cron schedule in CI/prod-like mode
- ingestion/transformation/validation DAGs support standalone manual invocation and master-triggered execution

Run window controls:

- define allowed execution windows per profile (`local`, `ci`, future `snowflake`)
- prevent overlapping critical runs via max active run policy
- preserve deterministic run context (`batch_id`, `pipeline_run_id`)

### 2) Configure retry behavior

Retry policy by task class:

- infrastructure/transient tasks (network/stage readiness): retries enabled
- deterministic validation failures: retries disabled
- dbt build/test tasks: limited retries only for non-deterministic execution failures
- publish/reporting tasks: bounded retry with short backoff

Baseline retry defaults:

- default retries: `2`
- retry delay: `5m`
- max retry delay cap: `20m`
- exponential backoff enabled for transient categories

Override controls:

- task-level retry overrides for known expensive or deterministic tasks
- profile-based retry policy map in runtime config

### 3) Define timeout and failure handling policies

Timeout policy:

- DAG-level `dagrun_timeout` per profile
- task execution timeouts by class:
  - ingestion dataset tasks
  - transformation layer tasks
  - validation gates
  - artifact publishing tasks

Failure handling policy:

- fail-fast for critical dependency path
- immediate downstream block when critical upstream fails
- structured failure classification:
  - `infra_transient`
  - `config_contract`
  - `data_quality`
  - `governance_block`
  - `unknown`

Operational response hooks:

- centralized failure callback for run metadata update
- standardized failure summary artifact generation
- optional alert integration hook (ready for observability phase)

### 4) Align failure behavior with governance rules

Governance alignment rules:

- critical validation and governance selector failures are blocking
- failure severities mapped to execution outcomes:
  - `critical` -> `FAILED` and block downstream
  - `high` -> configurable block in strict mode
  - `medium/low` -> warn with artifact evidence
- behavior aligned with Phase 5 failure policy contract and selector gates

Auditability alignment:

- record failure reason, gate name, selector, and stage in run metadata
- preserve lineage context (`pipeline_run_id`, timestamps, profile/target)
- produce reproducible evidence for issue and PR review

## Deliverables for Issue #70

- `airflow/config/phase6_profiles.yml` (schedule, retry, timeout policy sections)
- `airflow/dags/_fraudlens_phase6_common.py` (policy resolver + failure callbacks)
- `airflow/dags/fraudlens_phase6_pipeline_orchestration.py` (runtime policy wiring)
- `airflow/tests/test_phase6_runtime_policies.py`
- `documents/phase-6-plan/issue-70-scheduling-retries-failure-handling.md` (this plan)

## Commit Plan (Issue #70)

1. `feat(airflow-runtime): add phase 6 schedule modes and run windows for issue 70`
2. `feat(airflow-runtime): apply retry and timeout defaults by task category for issue 70`
3. `feat(airflow-runtime): enforce fail-fast critical path behavior for issue 70`
4. `docs(airflow-runtime): publish failure handling and escalation policy for issue 70`

## Acceptance Criteria Mapping

- schedule strategy defined: covered by schedule modes and run window policy
- retry behavior configured: covered by class-based retry contract and defaults
- timeout/failure handling policies defined: covered by timeout matrix and failure model
- governance-aligned behavior enforced: covered by severity mapping and blocking rules

## Risk Notes

- too-aggressive retries can increase runtime cost and hide root causes; keep deterministic failures non-retryable
- missing timeout boundaries can stall worker slots; enforce class-specific timeouts
- mixed strict/non-strict behavior can create inconsistent operational outcomes; profile policy must be explicit

## Open Decision Log

- confirm cron schedule for non-local profile baseline
- confirm strict-mode default in CI branch policy
- confirm where alert callback should integrate first (logs-only vs external channel)
