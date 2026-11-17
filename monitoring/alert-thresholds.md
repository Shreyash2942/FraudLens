# FraudLens Alert Threshold Guidance

Issue: `#75`  
Phase: `Phase 7 - Observability And Lineage`

These thresholds are Phase 7 starting points for local and production-like validation. They are intentionally conservative because FraudLens does not yet have long-running production baselines.

## Severity Model

| Severity | Meaning | Expected Action |
|---|---|---|
| `critical` | Pipeline output may be unavailable, invalid, or not auditable. | Investigate immediately before accepting the run. |
| `warning` | Pipeline completed with degraded observability, freshness, performance, or lineage. | Review during run validation and capture follow-up if repeated. |
| `informational` | Non-blocking operational event useful for trend analysis. | Track in dashboards or run evidence. |

## Pipeline Alerts

| Alert | Severity | Metric Expression Intent | Rationale |
|---|---|---|---|
| latest run failed | `critical` | `fraudlens_pipeline_run_status == 0` | A failed run blocks normal analytics readiness. |
| validation gate blocked publish | `critical` | `fraudlens_pipeline_quality_failure_total{severity="critical"} > 0` | Critical governance gates must remain blocking. |
| artifact completeness incomplete | `warning` | `fraudlens_pipeline_artifact_completeness < 1` | Missing artifacts reduce auditability and debugging quality. |
| stage failed | `critical` | `fraudlens_pipeline_stage_status == 0` | Operators need fast stage-level failure detection. |
| retry occurred | `informational` | `increase(fraudlens_pipeline_task_retry_total[1h]) > 0` | A successful run with retries may still indicate instability. |

## Performance Alerts

| Alert | Severity | Metric Expression Intent | Rationale |
|---|---|---|---|
| run duration high | `warning` | `fraudlens_pipeline_run_duration_seconds` exceeds configured baseline | Long runs may indicate runtime or data-volume issues. |
| stage duration high | `warning` | `fraudlens_pipeline_stage_duration_seconds` exceeds configured stage baseline | Stage duration isolates bottlenecks. |
| freshness lag high | `warning` | `fraudlens_pipeline_freshness_lag_seconds` exceeds accepted delay | Freshness drift reduces downstream usefulness. |

## Lineage Alerts

| Alert | Severity | Metric Expression Intent | Rationale |
|---|---|---|---|
| lineage event missing | `warning` | expected stage has no `fraudlens_pipeline_lineage_event_total` increase | Missing lineage weakens traceability. |
| lineage delivery failed | `warning` | `fraudlens_pipeline_lineage_delivery_total{status="failed"} > 0` | Local artifacts remain canonical, but Marquez visibility may be stale. |
| lineage delivery latency high | `warning` | `fraudlens_pipeline_lineage_delivery_latency_seconds` exceeds configured threshold | Slow delivery can delay visualization and debugging. |

## Service Health Alerts

| Alert | Severity | Metric Expression Intent | Rationale |
|---|---|---|---|
| Airflow unavailable | `critical` | `fraudlens_service_health_status{service_name="airflow"} == 0` | Operators cannot inspect or run orchestration reliably. |
| Prometheus unavailable | `warning` | `fraudlens_service_health_status{service_name="prometheus"} == 0` | Metrics collection and dashboards are degraded. |
| Grafana unavailable | `warning` | `fraudlens_service_health_status{service_name="grafana"} == 0` | Dashboard visibility is degraded. |
| MongoDB artifact storage unavailable | `warning` | `fraudlens_service_health_status{service_name="mongodb"} == 0` | Artifact lookup may fall back to local filesystem only. |
| Marquez unavailable | `warning` | `fraudlens_service_health_status{service_name="marquez"} == 0` | Lineage visualization is unavailable even if local events exist. |

## Baseline Policy

- Start with documented thresholds and dashboard visibility before enabling noisy automated alerts.
- Treat local JSONL artifacts as the fallback evidence source when external services are unavailable.
- Review thresholds after representative local runs create enough duration and freshness history.
- Keep alert labels aligned with `monitoring/metrics-catalog.md`.

