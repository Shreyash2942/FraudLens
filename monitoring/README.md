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
- `STANDARDS.md`
  - directory standards and integration expectations

## Planned Extensions

- Grafana dashboard definitions
- OpenLineage/Marquez integration payload mapping

## Prometheus Quick Start

1. Review `prometheus/prometheus.yml` for local scrape targets.
2. Render sample metrics:

```powershell
py monitoring\prometheus\render_fraudlens_metrics.py monitoring\prometheus\sample-metric-events.jsonl
```

3. Compare output with `prometheus/expected-fraudlens-metrics.prom`.
4. Use `prometheus/storage-verification.md` after Data-Lab Prometheus is running.
