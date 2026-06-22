# Observability Metrics and Dashboards Guide

Issue: #82 — Document Observability & Lineage Setup  
Phase: 7 — Observability & Lineage

## Purpose

Use this guide to understand FraudLens metrics, Prometheus collection, and Grafana dashboards.

## Metric Sources

FraudLens emits metric events from Airflow orchestration into:

```text
airflow/artifacts/observability/metrics/<workflow>/<run_stamp>/metric_events.jsonl
```

The Prometheus adapter converts those events into Prometheus exposition format.

## Canonical Metrics

| Metric | Purpose |
| --- | --- |
| `pipeline_run_status` | Shows latest run success or failure. |
| `pipeline_artifact_completeness` | Tracks expected vs completed run artifacts. |
| `pipeline_stage_status` | Shows stage-level health. |
| `pipeline_stage_duration_seconds` | Tracks stage performance and bottlenecks. |
| `pipeline_failure_total` | Counts failures by category. |
| `pipeline_quality_gate_total` | Tracks quality gate outcomes. |
| `pipeline_lineage_event_total` | Tracks lineage event generation. |
| `service_health_status` | Tracks platform service availability. |

## Prometheus Flow

1. Airflow emits metric JSONL.
2. Metric adapter renders Prometheus text.
3. Prometheus scrapes configured targets.
4. Grafana dashboards query Prometheus.

## Grafana Dashboards

| Dashboard | File | Use |
| --- | --- | --- |
| Pipeline overview | `fraudlens-pipeline-overview.json` | Run status, completeness, and recent pipeline state. |
| Pipeline performance | `fraudlens-pipeline-performance.json` | Stage duration and performance trends. |
| Failure quality | `fraudlens-failure-quality.json` | Failure categories and quality gate failures. |
| System health | `fraudlens-system-health.json` | Runtime and service health. |
| Lineage health | `fraudlens-lineage-health.json` | Lineage events and delivery health. |

## Validation Commands

```powershell
py monitoring\prometheus\render_fraudlens_metrics.py monitoring\prometheus\sample-metric-events.jsonl
py -m pytest tests\test_phase7_prometheus_scrape_config.py tests\test_phase7_grafana_dashboards.py tests\test_phase7_grafana_queries.py -q
```

## Operator Tips

- Use `run_profile`, `workflow`, and `dag_id` filters before drilling into task-level failures.
- Pair failure dashboard panels with Airflow `task_failure_classified` logs.
- Pair lineage health panels with Marquez delivery helper output.
