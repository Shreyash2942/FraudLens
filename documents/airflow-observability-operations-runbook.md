# Airflow Observability Operations Runbook

Issue: `#75`
Last updated: `2026-05-30`

## Purpose

Operate, validate, and troubleshoot orchestration observability artifacts emitted by FraudLens Airflow DAGs.

## Artifact Paths

Metrics artifacts:

- `airflow/artifacts/observability/metrics/<workflow>/<run_stamp>/metric_events.jsonl`

Lineage artifacts:

- `airflow/artifacts/observability/lineage/<workflow>/<run_stamp>/lineage_events.jsonl`

## What Gets Emitted

Current pipeline summary task emits:

- metric: `pipeline_run_status`
- metric: `pipeline_artifact_completeness`
- lineage event: `pipeline_run_completed`

## Validation Commands

Run local test suite:

```powershell
py -m pytest airflow/tests -q
```

Inspect recent observability artifacts:

```powershell
Get-ChildItem airflow\artifacts\observability -Recurse -File |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 20 FullName, LastWriteTime
```

Print latest metric events:

```powershell
Get-Content <path_to_metric_events.jsonl> -Tail 20
```

Print latest lineage events:

```powershell
Get-Content <path_to_lineage_events.jsonl> -Tail 20
```

## Profile Controls

Profile-level controls live in:

- `airflow/config/orchestration_profiles.yml`

Relevant keys under each profile `observability` block:

- `enabled`
- `emit_metrics`
- `emit_lineage`
- `metrics_namespace`
- `lineage_namespace`

## Troubleshooting

### No observability artifacts emitted

1. confirm run reached `publish_pipeline_summary`
2. confirm profile `observability.enabled` and stream toggles are true
3. confirm task logs for `metric_event_emitted` or `lineage_event_emitted`

### Metrics emitted but incomplete

1. inspect `pipeline_artifact_completeness` value
2. verify ingestion/transformation/validation summary artifact paths exist
3. inspect upstream DAG trigger and completion state

### Lineage event missing inputs/outputs

1. inspect `pipeline_summary.json` payload
2. verify path templating and run context values
3. rerun after root-cause correction and archive both runs for audit comparison
