# Airflow Orchestration Operations Runbook

Issue: `#73`
Last updated: `2026-05-30`

## Purpose

Operator-focused runbook for daily execution, troubleshooting, and recovery of FraudLens orchestration DAGs.

## Primary Commands

### Sync DAGs to Data-Lab container

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```

### Validate DAG import surface

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list"
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list-import-errors || true"
```

### Trigger pipeline run

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; \
  airflow dags trigger fraudlens_pipeline_orchestration \
  --conf '{\"profile\":\"local\",\"batch_id\":\"<batch_id>\"}'"
```

## Runtime Profiles

Profiles are defined in:

- `airflow/config/orchestration_profiles.yml`

Common values:

- `local`: local validation and development runs
- `ci`: CI-triggered non-interactive checks
- `snowflake` (future): warehouse-targeted profile

## Troubleshooting Guide

### Symptom: DAGs not visible in Airflow UI

Checks:

1. ensure container `fraudlens` is running
2. re-run DAG sync script
3. run `airflow dags list-import-errors`

Likely causes:

- stale DAG files in container
- Python import errors from DAG modules
- metadata DB unavailable

### Symptom: Metadata DB connection refused

Signature:

- `psycopg2.OperationalError`
- `localhost:5432 connection refused`

Action:

1. verify metadata DB service/process in container runtime
2. validate Airflow DB connection settings
3. re-run `airflow dags list` after DB restore

### Symptom: Validation gate fails

Action:

1. inspect validation task logs in Airflow
2. inspect output artifacts under `airflow/artifacts/orchestration/validation/<run_stamp>/`
3. classify failure category using failure artifact payload
4. remediate data/contract issue and rerun

### Symptom: Downstream tasks blocked

Interpretation:

- expected when upstream critical path fails
- dependents should become `upstream_failed`

Action:

1. inspect upstream failed task first
2. resolve root cause
3. trigger rerun from corrected runtime context

## Recovery Run Protocol

1. classify failure (`infra_transient`, `config_contract`, `data_quality`, `governance_block`, `unknown`)
2. confirm remediation applied
3. rerun with same batch when reproducibility is required
4. attach artifact paths and run metadata to incident notes

## Evidence And Audit

For every incident or failed run, capture:

- DAG ID + run ID
- profile + batch_id
- failure category
- artifact paths
- recovery trigger and final state
