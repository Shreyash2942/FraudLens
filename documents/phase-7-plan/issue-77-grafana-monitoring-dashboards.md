# Issue #77 Plan - Build Monitoring Dashboards With Grafana

Issue: `#77`

Phase: `Phase 7 - Observability And Lineage`

Status date: `2026-06-17`

## Description Alignment

Create Grafana dashboard assets that provide clear operational visibility into FraudLens pipeline runs, service health, quality gates, and lineage emission status.

This issue depends on the Prometheus metrics collection contract from issue `#76`. The dashboards should use Prometheus as their datasource and focus on operator-ready views rather than decorative reporting.

## Task Breakdown

### 1. Connect Grafana to Prometheus

Datasource setup:

- define Grafana datasource provisioning under `monitoring/grafana/provisioning/`
- use Prometheus as the primary datasource
- keep datasource UID/name stable for dashboard JSON references
- document Data-Lab Grafana and Prometheus endpoint assumptions
- include manual import fallback when provisioning is not available
- ensure dashboards can be opened in local development without Snowflake

Datasource validation:

- confirm Grafana can query Prometheus
- confirm `up` query returns expected scrape targets
- confirm `fraudlens_pipeline_run_status` or sample FraudLens metric is queryable
- document expected validation evidence in Phase 7 notes

### 2. Define dashboard views

- pipeline overview: latest run status, duration, stage outcomes, artifact completeness
- stage performance: ingestion, transformation, validation, and serving timing
- failure diagnostics: failure category counts, retry counts, blocked gates
- data quality: gate pass/fail trends and severity distribution
- lineage health: emitted lineage event counts and delivery failures
- platform health: Airflow, Prometheus, Marquez, MongoDB, and local runtime service checks

Recommended dashboard set:

| Dashboard | Purpose | Primary Metrics |
|---|---|---|
| `fraudlens-pipeline-overview` | run status and stage health | `fraudlens_pipeline_run_status`, `fraudlens_pipeline_stage_status`, `fraudlens_pipeline_artifact_completeness` |
| `fraudlens-pipeline-performance` | durations and bottlenecks | `fraudlens_pipeline_run_duration_seconds`, `fraudlens_pipeline_stage_duration_seconds`, `fraudlens_pipeline_task_attempt_total` |
| `fraudlens-failure-quality` | failures and gates | `fraudlens_pipeline_failure_total`, `fraudlens_pipeline_quality_gate_total`, `fraudlens_pipeline_quality_failure_total` |
| `fraudlens-system-health` | platform service health | `up`, `fraudlens_service_health_status`, resource metrics from issue `#76` |
| `fraudlens-lineage-health` | lineage emission and delivery | `fraudlens_pipeline_lineage_event_total`, `fraudlens_pipeline_lineage_delivery_total` |

### 3. Build pipeline run dashboards

Pipeline overview panels:

- latest pipeline status
- latest run duration
- stage status table
- artifact completeness gauge
- recent run status timeline
- failed stage or failure category summary
- latest batch/run identifiers as table fields where metric labels support them

Pipeline performance panels:

- run duration trend
- stage duration trend by stage
- slowest stage panel
- task attempts by status
- retry count by task and failure category
- freshness lag where available

### 4. Build system health dashboards

System health panels:

- Prometheus target health by scrape job
- Airflow availability
- Grafana availability
- Marquez availability
- MongoDB artifact storage availability
- Spark/Hive runtime availability
- CPU, memory, and disk panels where source metrics exist

System health rules:

- distinguish live scrape targets from planned/synthetic probes
- avoid showing empty resource panels as successful
- include datasource or query notes in dashboard metadata, not visible panel clutter

### 5. Track task durations and failures

Task visibility panels:

- task duration by task/stage when available
- task attempt count by status
- task retry count by task
- failure count by stage
- failure count by failure category
- validation gate failures by severity

Operational drilldown:

- variables for `environment`, `run_profile`, `workflow`, `stage`, and `status`
- optional variables for `dataset_name`, `quality_gate`, and `service_name`
- links or annotations pointing operators to logs/artifacts when supported

### 6. Build dashboard JSON assets

- store dashboard definitions under `monitoring/grafana/`
- use Prometheus datasource placeholders
- keep variables aligned with labels from issue `#75`
- include local and CI profile filters
- keep dashboards version-controlled as JSON
- separate datasource provisioning from dashboard JSON
- include sample screenshots or evidence references later if required

### 7. Add provisioning guidance

- document import/provisioning steps for Data-Lab Grafana
- include datasource dependency on Prometheus
- document expected panels and validation screenshots/evidence path
- document manual import flow for dashboard JSON
- document how to change datasource UID if the local Grafana instance differs
- document expected dashboard folder naming

### 8. Validate dashboards

- validate dashboard JSON structure
- smoke test with sample metrics where local services are available
- document known limitations when metrics are not yet populated
- validate dashboards reference the approved datasource UID
- validate PromQL expressions use metrics from issue `#75` and issue `#76`
- validate required dashboard variables exist
- validate dashboards do not depend on hard-coded batch IDs, run IDs, or hostnames

## Deliverables

- Grafana datasource provisioning file
- Grafana dashboard JSON files under `monitoring/grafana/dashboards/`
- dashboard provisioning notes under `monitoring/grafana/`
- README updates under `monitoring/`
- validation evidence checklist
- optional dashboard screenshots under `documents/assets/` if required for closeout

## Implementation Plan

1. Create Grafana folder structure and datasource provisioning convention.
2. Add pipeline overview dashboard JSON.
3. Add pipeline performance dashboard JSON for durations and task attempts.
4. Add failure and quality dashboard JSON.
5. Add system health dashboard JSON.
6. Add lineage health dashboard JSON if issue `#79` metric names are already stable, otherwise scaffold with planned queries.
7. Add dashboard validation checks for JSON shape, datasource references, variables, and metric references.
8. Add setup and validation runbook notes for Data-Lab Grafana.

## Commit Plan (Issue #77)

1. `docs(grafana): define dashboard architecture for issue 77`
2. `feat(grafana): add prometheus datasource provisioning for issue 77`
3. `feat(grafana): add pipeline overview dashboard for issue 77`
4. `feat(grafana): add pipeline performance dashboard for issue 77`
5. `feat(grafana): add failure and quality dashboard for issue 77`
6. `feat(grafana): add system health dashboard for issue 77`
7. `feat(grafana): add lineage health dashboard for issue 77`
8. `test(grafana): validate dashboard json assets for issue 77`
9. `test(grafana): validate dashboard prometheus queries for issue 77`
10. `docs(grafana): document dashboard provisioning and validation for issue 77`

## Acceptance Criteria Mapping

- Grafana connects to Prometheus: covered by datasource provisioning and validation
- pipeline run dashboards built: covered by overview and performance dashboards
- system health dashboards built: covered by system health dashboard
- task durations and failures tracked: covered by performance, failure, and quality dashboards
- Grafana dashboards provide real-time or near-real-time pipeline monitoring
- dashboards cover health, failures, performance, and lineage emission status
- panels use stable labels and metric names
- local setup steps are documented

## Risk Notes

- dashboard panels can become misleading if metric semantics are not locked first
- service-level panels depend on Data-Lab target availability
- too many panels can reduce operator signal; keep views role-focused
- PromQL queries can silently return empty results if datasource UID or label names drift
- resource panels may not be available until exporters or probes exist
- lineage dashboard may need final query adjustment after OpenLineage/Marquez work

## Open Decision Log

- confirm Grafana datasource UID/name convention, proposed: `prometheus`
- confirm whether dashboard provisioning is file-based or manual import
- confirm evidence format for dashboard validation
- confirm whether lineage dashboard is fully implemented in issue `#77` or finalized after issues `#79` and `#80`
- confirm whether dashboard screenshots should be stored in `documents/assets/`
