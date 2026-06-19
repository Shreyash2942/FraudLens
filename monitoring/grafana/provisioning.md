# Grafana Provisioning And Validation

Issue: `#77`  
Phase: `Phase 7 - Observability And Lineage`

Use this guide to provision or manually import FraudLens dashboards into a local Data-Lab Grafana instance.

## Provisioning Files

- datasource provisioning: `provisioning/datasources/prometheus.yaml`
- dashboard provider: `provisioning/dashboards/fraudlens.yaml`
- dashboard JSON assets: `dashboards/*.json`

## Datasource Validation

In Grafana, validate the Prometheus datasource:

1. Open the Prometheus datasource named `Prometheus`.
2. Confirm the datasource UID is `prometheus`.
3. Confirm the URL points to the local Data-Lab Prometheus endpoint.
4. Run a test query such as `up`.

Expected result:

- the datasource test succeeds
- `up` returns local scrape target series
- FraudLens sample metrics appear after the metric adapter exposes or renders events

## Manual Dashboard Import

If file provisioning is not available:

1. Open Grafana dashboard import.
2. Import each JSON file from `monitoring/grafana/dashboards/`.
3. Select the Prometheus datasource with UID or name `prometheus`.
4. Place dashboards in a `FraudLens` folder.

## Dashboard Validation

Validate these dashboards:

- `FraudLens Pipeline Overview`
- `FraudLens Pipeline Performance`
- `FraudLens Failure And Quality`
- `FraudLens System Health`
- `FraudLens Lineage Health`

Smoke test queries:

```promql
fraudlens_pipeline_run_status
fraudlens_pipeline_stage_duration_seconds
fraudlens_pipeline_failure_total
fraudlens_service_health_status
fraudlens_pipeline_lineage_event_total
up
```

## Evidence

For issue closeout or Phase 7 readiness, capture:

- datasource validation status
- imported dashboard list
- one successful panel query per dashboard
- any empty panels with the reason documented as unavailable metric source, no recent run, or optional service target

