# Issue #67 Plan - Build Ingestion Workflow Tasks

Issue: `#67`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Implement Airflow ingestion tasks that move raw batch files from MinIO into Bronze targets with controlled configuration, observability, and execution validation.

## Task Breakdown

### 1) Create ingestion task definitions

Planned task groups:

- `ingestion_prepare`
- `ingestion_dataset_fanout`
- `ingestion_postcheck`
- `ingestion_publish_summary`

Planned core tasks:

- resolve runtime profile, `batch_id`, `pipeline_run_id`
- validate dataset selection from governed dataset index
- run per-dataset Bronze load command (fan-out)
- aggregate task results and emit ingestion summary artifact

Airflow structure:

- DAG: `fraudlens_phase6_ingestion_workflow`
- TaskGroups:
  - `prepare_context`
  - `load_bronze_datasets`
  - `validate_ingestion_results`
  - `publish_ingestion_metadata`

### 2) Trigger raw file loading from MinIO to Snowflake Bronze

Execution model:

- reuse existing warehouse script contracts for local/runtime parity
- support profile-driven mode:
  - `local`: Spark/Hive compatible Bronze load path
  - `ci`: dry-run/contract validation mode
  - `snowflake` (future): stage and `COPY INTO` path

Command strategy per dataset:

- stage/file readiness check before load
- run dataset ingestion command with explicit `--batch-id`
- emit structured per-dataset status output

Planned dependency chain:

- `prepare_context` -> `check_input_assets` -> `load_bronze_datasets` -> `validate_ingestion_results`

### 3) Handle ingestion task configuration and parameters

Required run-time parameters:

- `batch_id` (default: latest valid batch)
- `profile` (`local`, `ci`, future `snowflake`)
- `datasets` (optional subset override)
- `strict_mode` (default true for critical checks)
- `max_parallel_datasets` (bounded fan-out)

Config artifacts:

- `airflow/config/phase6_profiles.yml`
- DAG-level `params` for overrides
- shared helper functions in `_fraudlens_phase6_common.py`

Policy decisions:

- invalid dataset names fail fast
- missing batch manifests block ingestion start
- empty dataset subset is rejected unless `allow_empty=true`

### 4) Validate ingestion task execution

Validation coverage:

- DAG import and parse checks
- task dependency contract validation
- parameter contract validation (required/default types)
- execution artifact presence check
- sampled local run evidence attached to issue

Expected evidence artifacts:

- ingestion run summary JSON
- per-dataset load status records
- failure log snippets for blocked scenarios

## Deliverables for Issue #67

- `airflow/dags/fraudlens_phase6_ingestion_workflow.py`
- `airflow/dags/_fraudlens_phase6_common.py` (extended for ingestion helpers)
- `airflow/config/phase6_profiles.yml` (ingestion runtime section)
- `airflow/tests/test_phase6_ingestion_dag.py`
- `documents/phase-6-plan/issue-67-ingestion-workflow-tasks.md` (this plan)

## Commit Plan (Issue #67)

1. `feat(airflow-ingestion): scaffold phase 6 ingestion dag and task groups for issue 67`
2. `feat(airflow-ingestion): add dataset-level bronze load tasks for issue 67`
3. `feat(airflow-ingestion): add stage and file readiness checks for issue 67`
4. `feat(airflow-ingestion): add ingestion completion gate and summary artifact for issue 67`
5. `test(airflow-ingestion): add ingestion dag import and config tests for issue 67`

## Acceptance Criteria Mapping

- ingestion task definitions created: covered by DAG/task group design and dataset fan-out model
- raw loading from MinIO to Bronze triggered: covered by profile-aware load command strategy
- configuration and parameters handled: covered by runtime parameter contract and policy decisions
- ingestion execution validated: covered by validation coverage and required evidence artifacts

## Risk Notes

- local Spark/Hive behavior can diverge from Snowflake load semantics; keep command builders profile-isolated
- uncontrolled fan-out can overload local runtime; enforce `max_parallel_datasets`
- missing batch/control files can create silent partial loads; treat as blocking in `strict_mode`

## Open Decision Log

- confirm source-of-truth list for ingestable datasets (`dataset_index.json` vs contract order)
- confirm default retry policy for dataset load tasks in local mode
- confirm whether ingestion DAG runs standalone or only via master Phase 6 DAG trigger
