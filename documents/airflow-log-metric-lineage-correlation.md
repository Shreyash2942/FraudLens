# Airflow Log, Metric, and Lineage Correlation

Issue: #78 — Integrate Pipeline Logging & Visibility  
Phase: 7 — Observability & Lineage

## Purpose

This guide explains how to move from an Airflow task log to the related metric and lineage artifacts during debugging or audit review.

## Correlation Keys

| Key | Source | Use |
| --- | --- | --- |
| `pipeline_run_id` | Run metadata and structured logs | Primary cross-signal run identifier. |
| `batch_id` | Run metadata and generated data paths | Connects execution to the generated batch. |
| `dag_id` | Airflow task context | Identifies the workflow that emitted the signal. |
| `task_id` | Airflow task context | Identifies the failing or emitting task. |
| `run_profile` | Orchestration profile | Separates local, CI, and future target-platform runs. |
| `workflow` | Metric and lineage emitters | Groups observability artifacts by FraudLens workflow. |
| `run_stamp` | Artifact paths | Locates per-run local evidence directories. |
| `artifact_reference` | Structured logs | Repository-relative pointer to the emitted evidence. |
| `failure_category` | Failure callback | Routes triage to infra, contract, quality, or governance handling. |

## Investigation Flow

1. Open the Airflow task log for the failed or suspicious task.
2. Find `task_failure_classified` when debugging failures.
3. Copy `failure_category` to identify the triage path.
4. Copy `artifact_reference` from `artifact_published`, `metric_event_emitted`, or `lineage_event_emitted`.
5. Inspect the referenced local artifact or configured MongoDB artifact record.
6. Use `pipeline_run_id`, `batch_id`, and `workflow` to compare logs with dashboard metrics and lineage events.

## Local Artifact Lookup

Use the helper when starting from a workflow name instead of a copied artifact reference:

```powershell
py scripts\locate_latest_airflow_artifacts.py --workflow pipeline --limit 10
```

Expected artifact families:

- `airflow/artifacts/orchestration/...` — run summaries, failure payloads, and stage evidence
- `airflow/artifacts/observability/metrics/...` — metric events for Prometheus-facing conversion
- `airflow/artifacts/observability/lineage/...` — lineage events for OpenLineage/Marquez-facing conversion

## Debugging Patterns

| Symptom | First Check | Follow-Up |
| --- | --- | --- |
| Dashboard shows a failed run | Airflow log `task_failure_classified` | Inspect failure artifact and upstream task logs. |
| Metrics missing for a run | Airflow log `metric_event_emitted` | Inspect `metric_events.jsonl` and profile observability toggles. |
| Lineage missing for a run | Airflow log `lineage_event_emitted` | Inspect `lineage_events.jsonl` and transformation summary payloads. |
| Artifact not found locally | Airflow log `artifact_backend` | Check whether profile uses MongoDB or dual artifact persistence. |
| Sensitive value appears in a log | Structured logger redaction rules | Add the key marker to `SENSITIVE_LOG_FIELD_MARKERS` and validate tests. |

## Operator Notes

- Prefer `artifact_reference` over absolute paths in tickets and audit notes.
- Do not paste raw credentials, connection strings, or tokens into issue comments.
- Keep `pipeline_run_id`, `batch_id`, and `failure_category` together when documenting incidents.
