# Airflow Observability And Lineage Design

Issue: `#74`
Last updated: `2026-05-30`

## Objective

Define the observability and lineage design contract for FraudLens orchestration runs so runtime behavior can be measured, audited, and handed off consistently.

## Design Scope

- orchestration run metrics emitted from Airflow task execution
- lineage event envelopes emitted from run context and stage summaries
- profile-based observability settings for local, CI, and future warehouse mode
- artifact-first storage model for reproducible review

## Runtime Signals

### Metric Event Types

- `pipeline_run_status`
- `pipeline_artifact_completeness`
- `pipeline_stage_dependency_health`
- `pipeline_failure_category_count`

### Lineage Event Types

- `pipeline_run_completed`
- `stage_transition`
- `quality_gate_result`

## Artifact Contract

- metrics stream root:
  - `airflow/artifacts/observability/metrics/<workflow>/<run_stamp>/metric_events.jsonl`
- lineage stream root:
  - `airflow/artifacts/observability/lineage/<workflow>/<run_stamp>/lineage_events.jsonl`

## Mandatory Labels / Fields

Metrics labels:

- `dag_id`
- `run_id`
- `batch_id`
- `run_profile`
- `run_target`
- `workflow`

Lineage envelope fields:

- `event_type`
- `event_time_utc`
- `job_name`
- `run_id`
- `batch_id`
- `run_profile`
- `inputs`
- `outputs`
- `status`

## Profile Integration

Observability behavior is controlled through `airflow/config/orchestration_profiles.yml` under per-profile `observability` blocks:

- `enabled`
- `emit_metrics`
- `emit_lineage`
- `metrics_namespace`
- `lineage_namespace`

## Failure Semantics

- observability emission must never hide task failure root causes
- emission helper failures are logged as warning events and do not override primary run status
- failure category from orchestration callbacks is propagated into metric/lineage payloads when available

## Implementation Boundary

Issue `#74` defines and documents contracts.
Issue `#75` implements emitter helpers and DAG integration using this design.
