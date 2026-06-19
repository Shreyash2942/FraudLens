# Airflow Logging Visibility Contract

Issue: #78 — Integrate Pipeline Logging & Visibility  
Phase: 7 — Observability & Lineage

## Purpose

FraudLens Airflow logs must provide enough structured context to debug pipeline failures, correlate logs with metrics, and trace emitted artifacts without exposing credentials or sensitive runtime values.

## Log Event Standards

Every structured orchestration log event must be emitted as single-line JSON with these baseline fields:

| Field | Required | Purpose |
| --- | --- | --- |
| `level` | Yes | Uppercase severity such as `INFO`, `WARNING`, or `ERROR`. |
| `event` | Yes | Stable machine-readable event name. |
| `timestamp_utc` | Yes | UTC event timestamp in ISO-8601 format. |
| `pipeline_run_id` | When available | Cross-signal run identifier. |
| `batch_id` | When available | Data batch associated with the event. |
| `dag_id` | When available | Airflow DAG source. |
| `task_id` | When available | Airflow task source. |
| `task_group` | When available | Airflow task group or stage grouping. |
| `run_profile` | When available | Runtime profile such as `local`, `ci`, or `prod`. |
| `run_target` | When available | Execution target such as local surrogate or target platform. |
| `workflow` | When available | FraudLens workflow namespace. |
| `stage` | When available | Pipeline stage being executed or observed. |
| `status` | When available | Event outcome such as `STARTED`, `SUCCESS`, or `FAILED`. |
| `failure_category` | Failure events | Operational failure grouping used for triage. |
| `artifact_reference` | Artifact events | Repository-relative pointer to generated evidence. |

## Event Categories

| Category | Example Events | Debugging Use |
| --- | --- | --- |
| Task execution | `task_failure_classified`, workflow summaries | Identify failing DAG/task and retry policy context. |
| Artifact publication | `artifact_published`, MongoDB fallback warnings | Locate persisted evidence for a run. |
| Metrics visibility | `metric_event_emitted` | Correlate task logs with Prometheus-facing metric events. |
| Lineage visibility | `lineage_event_emitted` | Correlate task logs with OpenLineage/Marquez-facing events. |

## Failure Categories

Failure logs must use the existing taxonomy:

- `infra_transient` — runtime, connectivity, or environment issues.
- `config_contract` — contract, configuration, or alignment issues.
- `data_quality` — validation, quality, or tag test issues.
- `governance_block` — governance or traceability enforcement issues.
- `unknown` — uncategorized failures requiring manual triage.

## Redaction Rules

Structured logs must redact values whose keys indicate secrets, credentials, tokens, passwords, or connection URIs. Redaction applies recursively to nested mappings and lists before the event is printed.

## Accessibility Requirements

- Airflow UI logs must show structured JSON events for task-level debugging.
- Artifact paths must be repository-relative when possible so operators can inspect local files quickly.
- Metric and lineage emitters must log the generated artifact reference for cross-signal investigation.
- Logs must avoid high-cardinality or raw payload dumps unless those payloads are persisted as artifacts.

## Acceptance Checklist

- Airflow task logs include stable JSON event fields.
- Failure logs include `failure_category`.
- Artifact writes log an `artifact_reference`.
- Metric and lineage emissions log correlated artifact references.
- Sensitive runtime fields are redacted before printing.
