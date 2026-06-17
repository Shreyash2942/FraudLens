# Airflow Orchestration Design Reference

Issue: `#73`
Last updated: `2026-05-30`

## Scope

Design reference for FraudLens Airflow orchestration DAG set and shared runtime contracts.

## DAG Portfolio

### 1) Master DAG

- File: `airflow/dags/fraudlens_pipeline_orchestration.py`
- DAG ID: `fraudlens_pipeline_orchestration`
- Role: top-level stage coordinator
- Stage chain:
  - `prepare_runtime`
  - `ingestion_layer`
  - `transformation_layer`
  - `validation_layer`
  - `publish_run_artifacts`

### 2) Ingestion DAG

- File: `airflow/dags/fraudlens_ingestion_workflow.py`
- DAG ID: `fraudlens_ingestion_workflow`
- Role: Bronze ingestion orchestration with dataset fan-out and strict-mode gates

### 3) Transformation DAG

- File: `airflow/dags/fraudlens_transformation_workflow.py`
- DAG ID: `fraudlens_transformation_workflow`
- Role: dbt layer execution gates (`bronze -> silver -> gold -> kpi`)

### 4) Validation DAG

- File: `airflow/dags/fraudlens_validation_workflow.py`
- DAG ID: `fraudlens_validation_workflow`
- Role: quality/governance checks and readiness output publishing

## Shared Runtime Contract

- Helper module: `airflow/dags/_fraudlens_orchestration_common.py`
- Profile contract: `airflow/config/orchestration_profiles.yml`
- Runtime policy categories include:
  - `infra_transient`
  - `ingestion_dataset`
  - `dbt_transform`
  - `validation_gate`
  - `deterministic_contract`
  - `artifact_publish`

## Standard Runtime Parameters

- `profile` (default `local`)
- `batch_id` (default `latest`)
- `pipeline_run_id` (derived from Airflow run metadata)
- `strict_mode` (ingestion behavior gate)

## Artifact Model

Runtime artifacts are emitted under:

- `airflow/artifacts/orchestration/ingestion/<run_stamp>/...`
- `airflow/artifacts/orchestration/transformation/<run_stamp>/...`
- `airflow/artifacts/orchestration/validation/<run_stamp>/...`
- `airflow/artifacts/orchestration/pipeline/<run_stamp>/...`
- `airflow/artifacts/orchestration/failures/<dag_id>/<run_stamp>/...`

## Operational Design Rules

- downstream progression is blocked on upstream failure by default (`all_success` semantics)
- critical quality/contract checks are fail-fast and non-retryable where policy defines `retries=0`
- run metadata should include canonical observability fields from shared helper (`pipeline_run_id`, `batch_id`, `run_profile`, timestamps)

## Related Docs

- `documents/airflow-orchestration-dependency-matrix.md`
- `documents/airflow-orchestration-operations-runbook.md`
- `airflow/runtime_failure_handling_policy.md`
