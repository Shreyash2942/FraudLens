# Orchestration Airflow

Status date: `2026-06-11`
Branch: `orchestration-airflow`
Milestone scope: `#65` with delivery across issues `#66`-`#75`

## Purpose

This document is the consolidated Phase 6 branch handoff for FraudLens Airflow orchestration.
It combines the design summary, dependency model, runbook guidance, observability notes,
readiness status, and closeout commit ledger for the `orchestration-airflow` branch.

## Final Branch Outcome

Implementation status: `COMPLETE FOR BRANCH CLOSEOUT`

What is now delivered:

- master Airflow orchestration DAG wiring for pipeline, ingestion, transformation, and validation
- shared runtime profile contract and retry/timeout/failure-category policies
- canonical run metadata emission across workflow summaries
- observability metric and lineage emission from pipeline orchestration
- MongoDB-only orchestration artifact persistence for `local`, `ci`, and `snowflake` profiles
- legacy local artifact cleanup utility and updated operator documentation

Current honesty check:

- branch implementation and documentation handoff: `READY`
- static test coverage and container smoke validation: `PASS`
- full production-like end-to-end success certification: `STILL REQUIRES FINAL HAPPY-PATH EXECUTION`

## Delivered Architecture

### DAG Portfolio

1. Master DAG
   - file: `airflow/dags/fraudlens_pipeline_orchestration.py`
   - DAG ID: `fraudlens_pipeline_orchestration`
   - role: top-level stage coordinator
   - stage flow: `prepare_runtime -> ingestion_layer -> transformation_layer -> validation_layer -> publish_run_artifacts`

2. Ingestion DAG
   - file: `airflow/dags/fraudlens_ingestion_workflow.py`
   - DAG ID: `fraudlens_ingestion_workflow`
   - role: Bronze ingestion orchestration with dataset fan-out and strict-mode gates

3. Transformation DAG
   - file: `airflow/dags/fraudlens_transformation_workflow.py`
   - DAG ID: `fraudlens_transformation_workflow`
   - role: dbt layer execution gates across `bronze -> silver -> gold -> kpi`

4. Validation DAG
   - file: `airflow/dags/fraudlens_validation_workflow.py`
   - DAG ID: `fraudlens_validation_workflow`
   - role: quality, governance, and readiness evidence execution

### Shared Runtime Contract

Primary shared helper:

- `airflow/dags/_fraudlens_orchestration_common.py`

Primary profile contract:

- `airflow/config/orchestration_profiles.yml`

Key shared concerns now handled centrally:

- repo root resolution
- orchestration profile loading
- runtime retry and timeout policy mapping
- canonical metadata shape
- failure classification callback wiring
- orchestration artifact persistence and retrieval
- observability metric and lineage emission

## Dependency And Gate Model

### Stage Dependency Chain

| From | To | Gate Type | Expected Failure Behavior |
|---|---|---|---|
| `prepare_runtime` | `ingestion_layer` | hard gate | downstream blocked |
| `ingestion_layer` | `transformation_layer` | hard gate | downstream blocked |
| `transformation_layer` | `validation_layer` | hard gate | downstream blocked |
| `validation_layer` | `publish_run_artifacts` | hard gate | summary stage not published on failure |

### Transformation Gate Order

| Layer | Must Wait For | Rule |
|---|---|---|
| `bronze` | runtime context + parse preflight | start of dbt chain |
| `silver` | `bronze` success | no partial progression |
| `gold` | `silver` success | no partial progression |
| `kpi` | `gold` success | terminal transform gate |

### Failure Categories

Shared callback logic classifies failures into:

- `infra_transient`
- `config_contract`
- `data_quality`
- `governance_block`
- `unknown`

## Runtime Profiles

Profiles are defined in `airflow/config/orchestration_profiles.yml`.

### `local`

- intended for local Spark/Hive development validation
- uses MongoDB artifact persistence
- default Mongo fallback URI is configured for the FraudLens container runtime

### `ci`

- intended for CI-triggered non-interactive validation
- uses MongoDB artifact persistence
- requires `FRAUDLENS_MONGODB_URI` in environments that do not use the local container default

### `snowflake`

- future warehouse-targeted profile scaffold
- uses MongoDB artifact persistence for orchestration evidence
- requires `FRAUDLENS_MONGODB_URI` when exercised outside local development

## Artifact And Observability Model

### Orchestration Evidence Storage

Orchestration evidence now persists to MongoDB collection:

- database: `datalab`
- collection: `orchestration_artifacts`

Stored artifact families include:

- pipeline runtime context and summary
- ingestion runtime context, dataset statuses, validation summary, and final summary
- transformation runtime context, stage statuses, and final summary
- validation check statuses and final summary
- failure artifacts
- observability metric events
- observability lineage events

### Artifact Path Contract

MongoDB documents keep the repository-style artifact path for traceability, for example:

- `airflow/artifacts/orchestration/pipeline/<run_stamp>/pipeline_summary.json`
- `airflow/artifacts/orchestration/ingestion/<run_stamp>/ingestion_summary.json`
- `airflow/artifacts/orchestration/transformation/<run_stamp>/transformation_summary.json`
- `airflow/artifacts/orchestration/validation/<run_stamp>/validation_summary.json`
- `airflow/artifacts/orchestration/failures/<dag_id>/<run_stamp>/<task_id>.json`
- `airflow/artifacts/observability/metrics/<workflow>/<run_stamp>/metric_events.jsonl`
- `airflow/artifacts/observability/lineage/<workflow>/<run_stamp>/lineage_events.jsonl`

### Current Observability Signals

Metrics:

- `pipeline_run_status`
- `pipeline_artifact_completeness`

Lineage events:

- `pipeline_run_completed`

## Operator Commands

### Sync DAGs Into The Container

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```

### Validate DAG Import Surface

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list"
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list-import-errors || true"
```

### Trigger Pipeline Run

```powershell
docker exec fraudlens sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; \
  airflow dags trigger fraudlens_pipeline_orchestration \
  --conf '{\"profile\":\"local\",\"batch_id\":\"<batch_id>\"}'"
```

### Inspect MongoDB Artifact Counts In Container

```powershell
docker exec fraudlens sh -lc "mongosh --quiet 'mongodb://admin:admin@localhost:27017/datalab?authSource=admin' --eval \"db=db.getSiblingDB('datalab'); print(db.orchestration_artifacts.countDocuments())\""
```

### Clean Legacy Local Artifact Folders

```powershell
python scripts/cleanup_airflow_artifacts.py --dry-run
python scripts/cleanup_airflow_artifacts.py
```

## Validation Status

### Verified In This Branch

- `py -m pytest airflow/tests -q`
  - result: `19 passed`
- Python compile validation for updated DAG/helper files: `PASS`
- container smoke test for Mongo-backed artifact write/read/list: `PASS`
- container smoke test confirmed no new local orchestration artifact files are created in Mongo-only mode
- Graphify project graph refreshed after final code changes

### Still Recommended Before Final Merge Sign-Off

1. execute one complete happy-path run of `fraudlens_pipeline_orchestration`
2. execute one controlled failure and recovery path against the live DAG set
3. capture final run IDs and MongoDB evidence references in merge notes

## Commit Ledger

Recent closeout commits on this branch:

1. `8122e77` `fix(airflow): harden phase 6 orchestration runtime wiring`
2. `a69bcac` `fix(dbt): make local hive transformations and tests phase 6 safe`
3. `bba28ae` `docs(airflow): refresh phase 6 readiness notes and plan references`
4. `9809efd` `feat(observability): add profile-level observability and lineage contract settings for issue 74`
5. `21df7e4` `docs(observability): publish metrics and lineage contracts for issue 74`
6. `366aaa6` `chore(observability): refresh monitoring asset index for issue 74`
7. `dee848e` `feat(airflow-observability): add shared metric and lineage emitters for issue 75`
8. `9a44d8a` `feat(airflow-observability): emit pipeline metrics and lineage artifacts for issue 75`
9. `11644b4` `test(airflow-observability): add observability emission coverage tests for issue 75`
10. `51afaff` `docs(airflow-observability): publish observability operations runbook for issue 75`
11. `a442eee` `feat(airflow): switch orchestration artifacts to mongodb only`
12. `241f080` `chore(airflow): clean up legacy local artifact folders`

## Consolidated Source Set

This branch document consolidates the operational content from:

- `documents/airflow-orchestration-design-reference.md`
- `documents/airflow-orchestration-dependency-matrix.md`
- `documents/airflow-orchestration-operations-runbook.md`
- `documents/airflow-orchestration-cicd-handoff-checklist.md`
- `documents/airflow-e2e-validation-runbook.md`
- `documents/airflow-orchestration-readiness-report.md`
- `documents/airflow-observability-lineage-design.md`
- `documents/airflow-observability-operations-runbook.md`

Those files remain useful as supporting references, but this document is the primary Phase 6 branch closeout and handoff file.
