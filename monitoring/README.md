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
- `marquez/`
  - Marquez environment defaults, visualization checklist, and lineage validation guidance
- `coverage/`
  - observability and lineage coverage matrix
- `STANDARDS.md`
  - directory standards and integration expectations
- Phase 7 setup documentation
  - `../documents/observability-lineage-setup-guide.md`
  - `../documents/observability-metrics-dashboards-guide.md`
  - `../documents/lineage-interpretation-guide.md`
  - `../documents/observability-lineage-troubleshooting-guide.md`
- OpenLineage documentation
  - `../documents/openlineage-tracking-contract.md`
  - `../documents/openlineage-airflow-dbt-runbook.md`
- Marquez documentation
  - `../documents/marquez-lineage-visualization-design.md`
  - `../documents/marquez-lineage-visualization-runbook.md`

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

## Marquez Quick Start

1. Review `marquez/marquez.env.example`.
2. Run `py scripts\check_marquez_health.py`.
3. Dry-run event delivery with `py scripts\deliver_openlineage_to_marquez.py --input <lineage_jsonl>`.
4. Send events with `--send` after dry-run validation succeeds.
5. Use `../documents/marquez-lineage-visualization-runbook.md` for UI evidence capture.

## Coverage Validation

1. Review `coverage/observability-lineage-coverage.json`.
2. Run `py scripts\validate_observability_lineage_coverage.py`.
3. Run `py -m pytest tests\test_phase7_coverage_matrix.py tests\test_phase7_documentation_complete.py -q`.
4. Use `../documents/observability-lineage-coverage-readiness-report.md` for closure evidence.
