# Monitoring

Monitoring, observability, and lineage assets for FraudLens pipeline operations.

## Current Contents

- `observability-contract.yaml`
  - canonical metric and lineage event contract
- `metrics-catalog.md`
  - Phase 7 metric catalog and label standards
- `alert-thresholds.md`
  - conservative alert threshold guidance
- `prometheus/`
  - Prometheus scrape configuration, FraudLens metric adapter assets, samples, and storage verification
- `grafana/`
  - Grafana datasource provisioning, dashboard provisioning, dashboards, and validation guidance
- `STANDARDS.md`
  - directory standards and integration expectations
- OpenLineage documentation
  - `../documents/openlineage-tracking-contract.md`
  - `../documents/openlineage-airflow-dbt-runbook.md`

## Planned Extensions

- Marquez visualization and delivery validation assets

## Prometheus Quick Start

1. Review `prometheus/prometheus.yml` for local scrape targets.
2. Render sample metrics:

```powershell
py monitoring\prometheus\render_fraudlens_metrics.py monitoring\prometheus\sample-metric-events.jsonl
```

3. Compare output with `prometheus/expected-fraudlens-metrics.prom`.
4. Use `prometheus/storage-verification.md` after Data-Lab Prometheus is running.

## Grafana Quick Start

1. Review `grafana/provisioning/datasources/prometheus.yaml`.
2. Import or provision dashboards from `grafana/dashboards/`.
3. Validate the Prometheus datasource UID is `prometheus`.
4. Use `grafana/provisioning.md` for dashboard smoke tests and evidence capture.
