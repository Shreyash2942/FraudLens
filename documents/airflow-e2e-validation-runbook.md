# Airflow End-to-End Validation Runbook

Issue: `#72`
Last updated: `2026-05-30`

## Purpose

Provide a reproducible procedure to validate the complete orchestration path:

`ingestion -> transformation -> validation`

for DAG `fraudlens_pipeline_orchestration`.

## Preconditions

- Docker container `fraudlens` is running.
- Airflow DAGs are synced to container path `/home/datalab/airflow/dags`.
- A test batch exists under `data/batches/<batch_id>/`.
- `FRAUDLENS_REPO_ROOT` resolves to `/home/datalab/fraudlens` inside the container.

## Test Batch Selection

Use one reproducible batch per execution window.

PowerShell helper:

```powershell
Get-ChildItem data\batches -Directory |
  Sort-Object Name |
  Select-Object -Last 1 -ExpandProperty Name
```

## Local Validation Sequence

### 1) Sync DAG files into the Data-Lab container

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```

### 2) Verify DAG import surface

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list"
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list-import-errors || true"
```

### 3) Trigger the pipeline DAG (happy-path)

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; \
  airflow dags trigger fraudlens_pipeline_orchestration \
    --conf '{\"profile\":\"local\",\"batch_id\":\"<batch_id>\"}'"
```

### 4) Observe task and DAG outcomes

```powershell
docker exec fraudlens sh -lc "airflow dags state fraudlens_pipeline_orchestration <run_id>"
docker exec fraudlens sh -lc "airflow tasks states-for-dag-run fraudlens_pipeline_orchestration <run_id>"
```

## Controlled Failure + Recovery Sequence

### 1) Trigger strict-mode failure path

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; \
  airflow dags trigger fraudlens_ingestion_workflow \
    --conf '{\"profile\":\"local\",\"batch_id\":\"<bad_or_missing_batch_id>\",\"strict_mode\":true}'"
```

Expected behavior:

- ingestion checks fail fast
- downstream dependent tasks become `upstream_failed`
- failure metadata is written to orchestration failure artifacts

### 2) Recovery run

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; \
  airflow dags trigger fraudlens_ingestion_workflow \
    --conf '{\"profile\":\"local\",\"batch_id\":\"<valid_batch_id>\",\"strict_mode\":false}'"
```

Expected behavior:

- transient validation blockers are bypassed only when policy allows
- run summary artifacts reflect non-strict recovery mode

## Artifact Checklist

Expected output roots when execution is available:

- `airflow/artifacts/orchestration/pipeline/<run_stamp>/pipeline_summary.json`
- `airflow/artifacts/orchestration/ingestion/<run_stamp>/ingestion_summary.json`
- `airflow/artifacts/orchestration/transformation/<run_stamp>/transformation_summary.json`
- `airflow/artifacts/orchestration/validation/<run_stamp>/validation_summary.json`
- `airflow/artifacts/orchestration/failures/<dag_id>/<run_stamp>/*.json` (failure path)

## Acceptance Checks

- Dependency order enforced (`ingestion -> transformation -> validation`).
- Layer gates enforced (`bronze -> silver -> gold -> kpi`).
- Validation executes only after transformation completion.
- Failure paths produce blocking behavior for downstream tasks.
- Run metadata includes `pipeline_run_id`, `batch_id`, `run_profile`, and timestamps.

## Notes

If Airflow metadata DB is unavailable, only static validation can be completed (DAG tests/import readiness). Runtime execution evidence must be marked as blocked with infrastructure root cause.
