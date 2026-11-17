# Observability and Lineage Troubleshooting Guide

Issue: #82 — Document Observability & Lineage Setup  
Phase: 7 — Observability & Lineage

## Purpose

Use this guide when metrics, dashboards, logs, lineage, or Marquez visualization do not behave as expected.

## Quick Triage

| Symptom | First Check | Next Action |
| --- | --- | --- |
| No Airflow artifacts | Airflow task logs | Search for `artifact_published` and task failure events. |
| Missing metrics | Metric JSONL path | Run the Prometheus renderer against the event file. |
| Grafana panels empty | Prometheus datasource | Confirm datasource UID is `prometheus`. |
| Missing lineage JSONL | Airflow profile settings | Confirm `observability.enabled` and `emit_lineage` are true. |
| Marquez delivery fails | `OPENLINEAGE_URL` | Run delivery helper without `--send` first. |
| Marquez UI empty | Marquez health | Run `py scripts\check_marquez_health.py`. |

## Airflow Logs

Search task logs for:

- `runtime_context_prepared`
- `artifact_published`
- `metric_event_emitted`
- `lineage_event_emitted`
- `task_failure_classified`

Required context fields:

- `dag_id`
- `task_id`
- `run_profile`
- `batch_id`
- `artifact_reference`
- `failure_category`

## Metrics

If Prometheus metrics are missing:

1. locate metric JSONL artifacts
2. run `render_fraudlens_metrics.py`
3. confirm expected metric names are present
4. confirm scrape target config is available
5. confirm Grafana queries match metric names

## Lineage

If OpenLineage payloads are missing:

1. inspect `lineage_events.jsonl`
2. confirm each event has `openlineage_event`
3. confirm `inputs` and `outputs` are populated
4. validate dbt manifest export if the issue is transformation lineage

## Marquez

If Marquez does not show lineage:

1. run `py scripts\check_marquez_health.py`
2. dry-run delivery with `scripts\deliver_openlineage_to_marquez.py`
3. send events only after dry-run succeeds
4. verify namespace and job names in the UI
5. inspect local JSONL if datasets are missing

## Coverage Validation

Run:

```powershell
py scripts\validate_observability_lineage_coverage.py
py -m pytest tests\test_phase7_coverage_matrix.py -q
```

If validation fails, inspect missing evidence paths in the script output.
