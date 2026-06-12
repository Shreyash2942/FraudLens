# Issue #71 Plan - Standardize Logging & Run Metadata

Issue: `#71`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Standardize logging and run metadata so every orchestration run is observable, diagnosable, and traceable for operational and governance needs.

## Task Breakdown

### 1) Standardize task logging approach

Logging standard model:

- structured log messages with consistent key/value payloads
- stage/task start, success, warning, and failure event logging
- command execution logs wrapped with normalized prefixes
- redaction-safe logging policy for secrets and sensitive tokens

Planned implementation controls:

- shared logging helpers in `_fraudlens_phase6_common.py`
- standardized log fields for all DAGs/task groups
- consistent log level usage (`INFO`, `WARNING`, `ERROR`)
- unified message templates for ingestion/transform/validation tasks

### 2) Capture run identifiers and execution metadata

Required run metadata fields:

- `pipeline_run_id`
- `batch_id`
- `dag_id`
- `task_id`
- `task_group`
- `run_profile`
- `run_target`
- `execution_date_utc`
- `started_at_utc`
- `ended_at_utc`
- `run_status`
- `failure_category` (if applicable)

Metadata capture strategy:

- resolve/generate run identifiers in `prepare_runtime`
- propagate context via task params/environment and XCom-safe payloads
- persist run summary artifact at end-of-run
- attach stage-level durations and selector counts where applicable

### 3) Align logs with auditability needs

Auditability alignment rules:

- include trace fields required by Phase 5 governance posture
- ensure failed gate logs include blocking selector and reason
- include lineage-supporting context (`source_system`, `pipeline_run_id`, stage)
- maintain immutable run summary artifact for review and PR evidence

Governance integration:

- logging vocabulary aligned with failure policy severity model
- record whether outcome is `SUCCESS`, `SUCCESS_WITH_WARNINGS`, or `FAILED`
- include governance checkpoint names in validation logs

### 4) Confirm log visibility in Airflow

Visibility checklist:

- task logs visible in Airflow UI for all phase 6 DAGs
- standardized fields appear in operator output consistently
- failure and retry events are clearly visible in graph and task logs
- run summary artifact path is discoverable from log output

Validation approach:

- import/parse checks for DAG logging wrappers
- sample local run to confirm field presence
- failure simulation run to confirm error visibility and metadata completeness

## Deliverables for Issue #71

- `airflow/dags/_fraudlens_phase6_common.py` (logging + metadata helper layer)
- `airflow/dags/fraudlens_phase6_pipeline_orchestration.py` (metadata propagation)
- `airflow/dags/fraudlens_phase6_ingestion_workflow.py` (logging adoption)
- `airflow/dags/fraudlens_phase6_transformation_workflow.py` (logging adoption)
- `airflow/dags/fraudlens_phase6_validation_workflow.py` (logging adoption)
- `airflow/tests/test_phase6_logging_metadata.py`
- `documents/phase-6-plan/issue-71-logging-run-metadata.md` (this plan)

## Commit Plan (Issue #71)

1. `feat(airflow-observability): define canonical run metadata schema for issue 71`
2. `feat(airflow-observability): implement shared logging and context wrappers for issue 71`
3. `feat(airflow-observability): persist run artifacts for ingestion transform validation for issue 71`
4. `test(airflow-observability): add metadata completeness checks for issue 71`

## Acceptance Criteria Mapping

- task logging standardized: covered by shared logging model and helper wrappers
- run identifiers/metadata captured: covered by required metadata fields and propagation strategy
- auditability alignment achieved: covered by governance-aligned logging rules
- log visibility confirmed in Airflow: covered by visibility checklist and validation approach

## Risk Notes

- overly verbose logs can reduce operational signal; keep structure concise and high-value
- missing metadata propagation across task boundaries can break traceability; enforce schema checks
- inconsistent logging between DAGs can weaken troubleshooting; adopt shared wrapper only

## Open Decision Log

- confirm final artifact location for run metadata summaries
- confirm whether metadata should also be emitted to external sink in this phase or deferred
- confirm retention window expectations for local Airflow logs
