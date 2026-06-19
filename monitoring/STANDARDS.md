# Monitoring Standards Index

This directory contains executable or contract assets for FraudLens observability and lineage.

## Current Assets

- `observability-contract.yaml`
  - canonical metric and lineage event field requirements
  - stream storage path patterns for artifact-first review
- `metrics-catalog.md`
  - Phase 7 metric names, types, labels, and dashboard usage
- `alert-thresholds.md`
  - Phase 7 alert threshold guidance
- `prometheus/`
  - Prometheus scrape configuration and FraudLens metric adapter assets
- `grafana/`
  - Grafana provisioning and dashboard assets
- `README.md`
  - scope and usage index

## Integration Targets

- Airflow orchestration run emitters
- Prometheus metric collection
- Grafana operational dashboards
- future OpenLineage/Marquez integration bridge

## Rule

When adding new observability assets, include:

1. field contract updates
2. sample event payload references
3. runbook update in `documents/`
4. metric catalog updates when names, labels, or dashboard semantics change

## Label Standards

- use governed labels from `observability-contract.yaml`
- avoid raw exception text, command text, SQL text, timestamps, and full file paths as labels
- put high-detail debugging context in logs or artifacts instead of metric labels
- keep Prometheus-facing metric names aligned with the `fraudlens_` prefix

## Prometheus Asset Standards

- keep `prometheus.yml` parseable as standard Prometheus YAML
- keep local service targets labeled with `environment` and `service_name`
- keep adapter mapping names aligned with `metrics-catalog.md`
- include sample input and expected output whenever mapping behavior changes
- update `prometheus/storage-verification.md` when storage evidence expectations change

## Grafana Asset Standards

- keep dashboard JSON files parseable and version-controlled
- use datasource UID `prometheus`
- keep dashboard variables aligned with governed metric labels
- do not hard-code run IDs, batch IDs, or local hostnames into PromQL queries
- update dashboard validation tests when dashboards or query conventions change
