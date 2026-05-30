# Runtime Failure Handling And Escalation Policy

This document defines schedule, retry, timeout, and fail-fast behavior for FraudLens orchestration DAGs.

## Schedule Strategy

- profile-driven schedule mode:
  - `manual`: no cron schedule
  - `ci_triggered`: no cron schedule, invoked by CI/job trigger
  - `daily`: cron schedule from profile runtime settings
- run windows are defined per profile:
  - `run_window_start_utc`
  - `run_window_end_utc`
- overlapping runs are constrained by `max_active_runs`.

## Retry And Timeout Policy

Task behavior is applied by runtime category:

- `infra_transient`
  - retries: `2`
  - retry delay: `5m` with exponential backoff
  - timeout: `15m`
- `ingestion_dataset`
  - retries: `1`
  - retry delay: `5m` with exponential backoff
  - timeout: `30m`
- `dbt_transform`
  - retries: `1`
  - retry delay: `5m` with exponential backoff
  - timeout: `45m`
- `validation_gate`
  - retries: `0`
  - timeout: `20m`
- `deterministic_contract`
  - retries: `0`
  - timeout: `10m`
- `artifact_publish`
  - retries: `1`
  - retry delay: `2m`
  - timeout: `10m`

Each orchestration DAG also uses `dagrun_timeout_minutes` from profile runtime settings.

## Fail-Fast Policy

- critical path validation and contract tasks are non-retryable (`retries=0`).
- downstream stages remain blocked by default Airflow `all_success` trigger behavior.
- deterministic governance/contract failures immediately stop critical path progression.

## Failure Classification

On task failure, shared callback logic classifies failures into:

- `infra_transient`
- `config_contract`
- `data_quality`
- `governance_block`
- `unknown`

Failure artifacts are emitted to:

- `airflow/artifacts/orchestration/failures/<dag_id>/<run_stamp>/<task_id>.json`

## Escalation Workflow

1. Inspect task logs in Airflow UI.
2. Inspect failure artifact JSON for category and error payload.
3. If `infra_transient`, retry run in allowed window.
4. If `config_contract`, `data_quality`, or `governance_block`, fix root cause before rerun.
