# Grafana Monitoring Dashboards

Issue: `#77`  
Phase: `Phase 7 - Observability And Lineage`

This folder contains Grafana datasource provisioning, dashboard provisioning, and dashboard JSON assets for FraudLens operational monitoring.

## Architecture

Grafana uses Prometheus as the primary datasource for Phase 7 monitoring.

Flow:

1. FraudLens emits canonical metric events.
2. Prometheus collects FraudLens and service metrics.
3. Grafana reads Prometheus through a stable datasource UID.
4. Dashboards show pipeline status, duration, failures, service health, and lineage health.

## Datasource Convention

- datasource name: `Prometheus`
- datasource UID: `prometheus`
- datasource type: `prometheus`
- default URL: `http://prometheus:9090`

Local users can override the URL in Grafana after import if Data-Lab exposes Prometheus at a different address.

## Dashboard Set

| Dashboard | File | Purpose |
|---|---|---|
| Pipeline Overview | `dashboards/fraudlens-pipeline-overview.json` | Latest run status, stage health, artifact completeness, and failures. |
| Pipeline Performance | `dashboards/fraudlens-pipeline-performance.json` | Run duration, stage duration, task attempts, and retries. |
| Failure And Quality | `dashboards/fraudlens-failure-quality.json` | Failure categories and quality gate outcomes. |
| System Health | `dashboards/fraudlens-system-health.json` | Prometheus targets and platform service health. |
| Lineage Health | `dashboards/fraudlens-lineage-health.json` | Lineage event emission and delivery status. |

## Variables

Dashboards use common variables where practical:

- `environment`
- `run_profile`
- `workflow`
- `stage`
- `status`
- `service_name`

## Validation

Static validation checks should confirm:

- dashboards parse as JSON
- every dashboard references datasource UID `prometheus`
- required variables are present
- PromQL expressions use `fraudlens_` metrics or the Prometheus `up` metric
- dashboards do not hard-code specific run IDs or batch IDs

