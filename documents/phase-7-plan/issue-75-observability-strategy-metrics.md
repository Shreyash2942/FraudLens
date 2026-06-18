# Issue #75 Plan - Define Observability Strategy And Metrics

Issue: `#75`  
Phase: `Phase 7 - Observability And Lineage`  
Status date: `2026-06-17`

## Description Alignment

Define the observability strategy, metric taxonomy, operational signals, labels, and acceptance model for FraudLens pipeline monitoring.

This issue is design-first. It establishes the contract that later Prometheus, Grafana, logging, OpenLineage, and Marquez workstreams implement.

## Task Breakdown

### 1. Inventory existing signals

Existing Phase 6 observability inputs:

- `airflow/dags/_fraudlens_orchestration_common.py` emits metric and lineage events.
- `airflow/config/orchestration_profiles.yml` controls observability by profile.
- `monitoring/observability-contract.yaml` defines the current metric and lineage event contract.
- `documents/airflow-observability-lineage-design.md` documents the first design boundary.
- `documents/airflow-observability-operations-runbook.md` documents current artifact inspection.

Inventory work:

- review current metric event names, labels, and emitted fields
- review current lineage event names and required lineage fields
- identify gaps by pipeline layer: ingestion, transformation, validation, serving/KPI
- identify gaps by platform service: Airflow, Spark/Hive, MongoDB artifact storage, Prometheus, Grafana, Marquez
- preserve local JSONL artifacts as canonical review evidence even when service integrations are enabled

### 2. Define metric taxonomy

Pipeline execution metrics:

- `pipeline_run_status`: final run status as a numeric gauge
- `pipeline_run_duration_seconds`: total orchestration runtime
- `pipeline_stage_status`: status by stage
- `pipeline_stage_duration_seconds`: runtime by stage
- `pipeline_task_attempt_total`: task attempts by task and status
- `pipeline_task_retry_total`: retry count by task and failure category
- `pipeline_failure_total`: failures by stage and failure category

Data and governance metrics:

- `pipeline_artifact_completeness`: completed artifacts divided by expected artifacts
- `pipeline_dataset_processed_total`: processed dataset count by stage
- `pipeline_quality_gate_total`: quality/governance gate outcome count
- `pipeline_quality_failure_total`: failed quality checks by severity or gate
- `pipeline_freshness_lag_seconds`: lag between batch timestamp and observed completion where available

Lineage health metrics:

- `pipeline_lineage_event_total`: lineage events emitted by event type and status
- `pipeline_lineage_delivery_total`: external lineage delivery attempts by status
- `pipeline_lineage_delivery_latency_seconds`: delivery latency when an external endpoint is configured

System-level metrics:

- `service_health_status`: service availability by service name
- `service_response_time_seconds`: health check response time
- `runtime_cpu_utilization_percent`: CPU utilization when available from runtime/exporter
- `runtime_memory_utilization_percent`: memory utilization when available from runtime/exporter
- `runtime_disk_free_bytes`: available storage for local runtime paths when available

### 3. Define labels and cardinality rules

Required labels:

- `environment`
- `run_profile`
- `run_target`
- `dag_id`
- `workflow`
- `stage`
- `status`

Controlled labels:

- `task_id`
- `batch_id`
- `dataset_name`
- `failure_category`
- `quality_gate`
- `severity`
- `service_name`
- `lineage_namespace`
- `lineage_event_type`

Cardinality controls:

- do not use raw exception messages as labels
- do not use full file paths as labels
- do not use command text or SQL text as labels
- do not use timestamps as labels
- keep `dataset_name`, `task_id`, and `quality_gate` values governed by project contracts
- place high-detail debug context in logs and artifacts instead of metric labels

### 4. Define operational objectives

Operational goals:

- show whether the latest pipeline run succeeded, failed, or completed with warnings
- identify which stage caused a failed or slow run
- identify failed quality gates and failure categories without reading every task log first
- confirm required run artifacts were created
- confirm lineage events were emitted and, later, delivered to Marquez through OpenLineage
- confirm core platform services are reachable before or during a run
- keep enough evidence for governance and audit review

Alerting threshold candidates:

- critical: latest scheduled or expected run failed
- critical: validation gate failure blocks publish
- warning: run duration exceeds rolling baseline or configured threshold
- warning: artifact completeness drops below `1.0`
- warning: lineage delivery fails while local lineage artifact exists
- warning: service health check fails for Prometheus, Grafana, Marquez, MongoDB, or Airflow
- informational: retry occurred but final task status is successful

### 5. Align with implementation workstreams

Issue dependency alignment:

- issue `#76` uses this taxonomy to expose Prometheus-compatible metrics
- issue `#77` uses these metric names and labels for Grafana dashboard variables and panels
- issue `#78` uses the cardinality rules to keep detailed debug context in logs and artifacts
- issue `#79` uses lineage health metrics to validate OpenLineage emission
- issue `#80` uses lineage delivery metrics and labels to validate Marquez visibility
- issue `#81` uses the metric catalog as the coverage checklist
- issue `#82` consolidates the final strategy into the Phase 7 handoff

## Deliverables

- updated `monitoring/observability-contract.yaml` with Phase 7 metric categories and label rules
- Phase 7 metric catalog under `monitoring/`, expected as `monitoring/metrics-catalog.md`
- optional alert threshold catalog under `monitoring/`, expected as `monitoring/alert-thresholds.md`
- documentation updates in this planning workspace
- issue-specific validation checklist

## Implementation Plan

1. Update the monitoring contract with Phase 7 metric categories, labels, and cardinality rules.
2. Add a human-readable metric catalog that explains each metric, type, labels, and intended dashboard usage.
3. Add optional alert threshold guidance tied to operational goals.
4. Update `monitoring/README.md` and `monitoring/STANDARDS.md` to reference the new strategy assets.
5. Add a lightweight validation check for the strategy assets.
6. Record issue `#75` evidence in this plan and prepare the branch for the next sub-issue.

## Commit Plan (Issue #75)

1. `docs(observability): define phase 7 metric strategy for issue 75`
2. `docs(monitoring): add metric catalog and label standards for issue 75`
3. `docs(monitoring): add alert threshold guidance for issue 75`
4. `test(monitoring): validate observability strategy assets for issue 75`

## Acceptance Criteria Mapping

- key pipeline metrics identified: covered by pipeline execution metrics
- failures and duration identified: covered by run, stage, task, retry, and failure metrics
- system-level metrics identified: covered by service health and runtime resource metrics
- optional alerting thresholds defined: covered by threshold candidates
- metrics aligned with operational goals: covered by operational goals and issue dependency alignment
- later Prometheus, Grafana, OpenLineage, and Marquez workstreams have a stable contract

## Risk Notes

- metric names can drift if Prometheus work starts before the taxonomy is stable
- high-cardinality labels can make dashboards noisy and expensive
- local artifact behavior must remain useful even when external services are offline
- CPU and memory metrics may depend on Data-Lab exporters, so the strategy should mark source availability clearly
- alert thresholds should start conservative because this portfolio project may not have long production baselines

## Open Decision Log

- confirm exact Prometheus metric prefix, proposed: `fraudlens_`
- confirm whether service health metrics come from exporters, synthetic probes, or both
- confirm whether serving-layer metrics are limited to KPI outputs until Phase 9
- confirm whether alert thresholds remain documentation-only in issue `#75` or get executable rules in issue `#76` or `#77`
