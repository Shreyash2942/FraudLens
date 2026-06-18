# FraudLens Metrics Catalog

Issue: `#75`  
Phase: `Phase 7 - Observability And Lineage`

This catalog defines the Phase 7 metrics used by Prometheus collection, Grafana dashboards, coverage validation, and observability documentation.

## Naming Convention

- Prometheus metric prefix: `fraudlens_`
- Canonical event metric names remain unprefixed in local JSONL artifacts.
- Prometheus-facing metric names use the prefix plus the canonical metric name.
- Example: local `pipeline_run_status` becomes `fraudlens_pipeline_run_status`.

## Label Rules

Required labels:

- `environment`
- `run_profile`
- `run_target`
- `dag_id`
- `workflow`
- `stage`
- `status`

Controlled optional labels:

- `task_id`
- `batch_id`
- `dataset_name`
- `failure_category`
- `quality_gate`
- `severity`
- `service_name`
- `lineage_namespace`
- `lineage_event_type`

Blocked label sources:

- raw exception messages
- full file paths
- command text
- SQL text
- timestamps

High-detail debug context belongs in logs and artifacts, not metric labels.

## Pipeline Execution Metrics

| Metric | Type | Core Labels | Purpose |
|---|---|---|---|
| `pipeline_run_status` | gauge | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `status` | Shows final pipeline status as `1` for success and `0` for failure. |
| `pipeline_run_duration_seconds` | gauge | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `status` | Tracks total orchestration runtime. |
| `pipeline_stage_status` | gauge | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `stage`, `status` | Shows stage-level success, failure, or blocked state. |
| `pipeline_stage_duration_seconds` | gauge | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `stage`, `status` | Tracks ingestion, transformation, validation, and publish duration. |
| `pipeline_task_attempt_total` | counter | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `stage`, `task_id`, `status` | Counts task attempts by status. |
| `pipeline_task_retry_total` | counter | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `stage`, `task_id`, `failure_category` | Counts retries by task and failure type. |
| `pipeline_failure_total` | counter | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `stage`, `failure_category` | Counts blocking failures by stage and category. |

## Data And Governance Metrics

| Metric | Type | Core Labels | Purpose |
|---|---|---|---|
| `pipeline_artifact_completeness` | gauge | `environment`, `run_profile`, `run_target`, `dag_id`, `workflow`, `status` | Tracks completed artifacts divided by expected artifacts. |
| `pipeline_dataset_processed_total` | counter | `environment`, `run_profile`, `run_target`, `workflow`, `stage`, `dataset_name`, `status` | Counts datasets processed by stage. |
| `pipeline_quality_gate_total` | counter | `environment`, `run_profile`, `run_target`, `workflow`, `quality_gate`, `severity`, `status` | Counts quality and governance gate outcomes. |
| `pipeline_quality_failure_total` | counter | `environment`, `run_profile`, `run_target`, `workflow`, `quality_gate`, `severity` | Counts failed quality checks. |
| `pipeline_freshness_lag_seconds` | gauge | `environment`, `run_profile`, `run_target`, `workflow`, `stage`, `dataset_name` | Tracks lag between batch time and observed completion where available. |

## Lineage Health Metrics

| Metric | Type | Core Labels | Purpose |
|---|---|---|---|
| `pipeline_lineage_event_total` | counter | `environment`, `run_profile`, `run_target`, `workflow`, `stage`, `lineage_namespace`, `lineage_event_type`, `status` | Counts lineage events emitted locally. |
| `pipeline_lineage_delivery_total` | counter | `environment`, `run_profile`, `run_target`, `workflow`, `lineage_namespace`, `status` | Counts external OpenLineage delivery attempts. |
| `pipeline_lineage_delivery_latency_seconds` | gauge | `environment`, `run_profile`, `run_target`, `workflow`, `lineage_namespace`, `status` | Tracks external lineage delivery latency. |

## System Health Metrics

| Metric | Type | Core Labels | Purpose |
|---|---|---|---|
| `service_health_status` | gauge | `environment`, `service_name`, `status` | Shows service availability as `1` for healthy and `0` for unhealthy. |
| `service_response_time_seconds` | gauge | `environment`, `service_name`, `status` | Tracks health probe response duration. |
| `runtime_cpu_utilization_percent` | gauge | `environment`, `service_name` | Tracks CPU utilization when exporter data exists. |
| `runtime_memory_utilization_percent` | gauge | `environment`, `service_name` | Tracks memory utilization when exporter data exists. |
| `runtime_disk_free_bytes` | gauge | `environment`, `service_name` | Tracks free local runtime storage when exporter data exists. |

## Dashboard Usage

- Pipeline overview uses run status, stage status, artifact completeness, and failure counts.
- Pipeline performance uses run duration, stage duration, task attempts, retries, and freshness lag.
- Failure and quality dashboards use failure totals and quality gate metrics.
- System health dashboards use service health, response time, and runtime resource metrics.
- Lineage health dashboards use lineage event and delivery metrics.

