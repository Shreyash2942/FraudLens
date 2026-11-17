# Issue #78 Plan - Integrate Pipeline Logging And Visibility

Issue: `#78`

Phase: `Phase 7 - Observability And Lineage`

Status date: `2026-06-17`

## Description Alignment

Improve pipeline debugging and operational visibility by standardizing log discovery, log context, run summaries, and failure investigation workflows.

This issue extends the Phase 6 logging and run metadata foundation. It should make Airflow task logs, run artifacts, metric events, and lineage events easy to correlate during a failed or slow pipeline run.

## Task Breakdown

### 1. Review current logging contract

Existing Phase 6 baseline:

- structured logging and metadata were planned in issue `#71`
- Airflow DAGs use shared orchestration helpers in `airflow/dags/_fraudlens_orchestration_common.py`
- profile settings live in `airflow/config/orchestration_profiles.yml`
- run, metric, and lineage artifacts are persisted for supported profiles
- `documents/airflow-observability-operations-runbook.md` documents current artifact inspection

Review work:

- verify task logs include run identifiers, batch identifiers, profile, target, workflow, stage, task, and status
- verify failure logs include failure category and enough command context to debug without leaking secrets
- verify retry logs make retry count and task class visible
- verify artifact publish logs include paths or MongoDB artifact references
- identify gaps between Airflow logs, metric events, lineage events, and run summary artifacts

Required log context fields:

- `pipeline_run_id`
- `batch_id`
- `dag_id`
- `task_id`
- `task_group` or `stage`
- `workflow`
- `run_profile`
- `run_target`
- `event_type`
- `status`
- `failure_category` when applicable
- `artifact_reference` when applicable

### 2. Improve log visibility

Airflow UI visibility:

- validate task logs are available from the Airflow UI for master, ingestion, transformation, and validation workflows
- document how to navigate from DAG run to failed task logs
- document expected log markers for start, success, warning, retry, failure, metric emission, lineage emission, and artifact publication
- document how to identify the latest failed task from the Airflow grid/graph view

Artifact visibility:

- document local filesystem artifact paths for legacy/local inspection
- document MongoDB artifact collection lookup for profiles that persist artifacts to MongoDB
- ensure run summary artifacts reference metric and lineage artifact locations
- add or plan a helper command/script for locating latest run artifacts if current manual steps are too slow

Log discovery commands:

- list recent Airflow task logs or artifact files
- print latest run summary
- print latest metric and lineage events for a workflow
- locate artifacts by `pipeline_run_id` or `batch_id`

### 3. Align debug workflow

Debug triage flow:

1. identify failed DAG run and failed task in Airflow UI
2. copy `pipeline_run_id`, `batch_id`, `workflow`, `stage`, and `task_id`
3. inspect task log around start, retry, failure, and artifact markers
4. inspect run summary artifact for final status and stage status
5. inspect metric events for failure category, duration, and artifact completeness
6. inspect lineage events for last emitted stage transition or pipeline completion event
7. classify the failure as infra transient, deterministic contract, validation gate, artifact publish, or unknown
8. archive the log/artifact references needed for issue or PR evidence

Layer-specific debugging:

- ingestion: source asset checks, dataset fan-out, Bronze load command, validation summary
- transformation: dbt selector execution, Bronze/Silver/Gold/KPI stage status, dbt parse/build failure
- validation: quality gate severity, failure policy result, blocking selector
- publish/observability: artifact persistence, metric emission, lineage emission

Correlation rules:

- `pipeline_run_id` is the primary correlation key
- `batch_id` links source data, transformations, validation, and dashboard context
- `workflow` and `stage` link task logs to metric labels
- `lineage_namespace` and `run_id` link local lineage artifacts to OpenLineage/Marquez workstreams
- detailed exception text belongs in logs/artifacts, not metric labels

### 4. Validate logging coverage

Automated validation:

- add or update tests for required run metadata fields
- validate shared logging helpers include required context keys
- validate failure-category propagation into run summaries and observability events
- validate secret-like values are not written into standard log payload examples
- validate documentation references expected log/artifact inspection commands

Manual validation:

- run or inspect an Airflow task log in the UI
- confirm start/success/failure markers are visible
- confirm failed task logs show enough context to identify the failing stage
- confirm run summary links to metrics and lineage artifacts
- confirm MongoDB artifact lookup works for profiles where MongoDB is configured

### 5. Standardize logging format where needed

Logging format rules:

- use structured key/value payloads for operational events
- use stable event names such as `task_started`, `task_succeeded`, `task_failed`, `task_retried`, `artifact_published`, `metric_event_emitted`, and `lineage_event_emitted`
- include required context fields where available
- use `INFO` for normal milestones, `WARNING` for degraded non-blocking conditions, and `ERROR` for blocking failures
- redact secrets, connection strings, tokens, passwords, and raw credentials
- keep command output useful but bounded

Format gap remediation:

- update shared helpers first when common behavior is missing
- update DAG-specific logs only where the shared helper cannot supply enough context
- keep existing Phase 6 naming stable unless a field is clearly missing or ambiguous

### 6. Align with metrics, dashboards, and lineage

Cross-workstream alignment:

- issue `#76` Prometheus metrics should summarize the same status/failure categories that logs explain
- issue `#77` Grafana panels should point operators toward the log/artifact lookup workflow
- issue `#79` OpenLineage events should share run identifiers with logs
- issue `#81` coverage validation should confirm logs, metrics, and lineage can be correlated for success and failure cases

## Deliverables

- logging visibility runbook updates under `documents/`
- metadata and log coverage tests
- optional helper script for locating latest run artifacts
- updated references from Phase 7 docs
- Airflow UI validation checklist
- debugging correlation checklist
- secret redaction and safe logging expectations

## Implementation Plan

1. Inventory current Airflow log fields and run artifact references.
2. Define the Phase 7 required log context and event vocabulary.
3. Update shared logging/run metadata helpers only where gaps exist.
4. Add or update artifact lookup guidance for filesystem and MongoDB-backed runs.
5. Add tests for required metadata, failure category propagation, and safe logging expectations.
6. Add manual Airflow UI validation checklist.
7. Update the observability operations runbook with debugging flows and correlation commands.
8. Record evidence requirements for issue `#81` validation.

## Commit Plan (Issue #78)

1. `docs(logging): define phase 7 log visibility contract for issue 78`
2. `feat(airflow-logging): add missing structured log context for issue 78`
3. `feat(airflow-logging): improve artifact reference logging for issue 78`
4. `feat(airflow-logging): add latest run artifact lookup helper for issue 78`
5. `test(airflow-logging): validate required log metadata for issue 78`
6. `test(airflow-logging): validate failure category propagation for issue 78`
7. `test(airflow-logging): validate safe logging redaction for issue 78`
8. `docs(airflow): document ui log inspection workflow for issue 78`
9. `docs(observability): document log metric lineage correlation for issue 78`

## Acceptance Criteria Mapping

- Airflow logs validated for tasks: covered by Airflow UI visibility and manual validation
- logging format standardized where needed: covered by logging format rules and remediation plan
- logs accessible in UI: covered by Airflow UI visibility checklist
- logs aligned with debugging needs: covered by debug triage flow and layer-specific debugging
- log context correlates with metrics and lineage events
- failure investigation steps are documented
- run artifacts remain audit-friendly

## Risk Notes

- log verbosity can bury important operational signals
- storing paths or exception text as metric labels must be avoided
- MongoDB and local filesystem artifact views must stay logically consistent
- too much helper logic in DAG files can make orchestration harder to read
- UI validation depends on Data-Lab Airflow availability, so CI should focus on contract checks
- redaction rules must be tested before adding richer command context

## Open Decision Log

- confirm whether a latest-run artifact locator script is needed, proposed yes if MongoDB lookup is not enough
- confirm whether logs should be exported beyond Airflow in Phase 7
- confirm minimum fields required in every failure log event
- confirm whether Airflow UI screenshot evidence is required for closeout
- confirm whether log retention is controlled by Data-Lab defaults or documented separately
