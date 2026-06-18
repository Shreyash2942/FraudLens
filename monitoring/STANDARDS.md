# Monitoring Standards Index

This directory contains executable or contract assets for FraudLens observability and lineage.

## Current Assets

- `observability-contract.yaml`
  - canonical metric and lineage event field requirements
  - stream storage path patterns for artifact-first review
- `metrics-catalog.md`
  - Phase 7 metric names, types, labels, and dashboard usage
- `README.md`
  - scope and usage index

## Integration Targets

- Airflow orchestration run emitters
- future Prometheus exporter adaptation
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
