# Monitoring Standards Index

This directory contains executable or contract assets for FraudLens observability and lineage.

## Current Assets

- `observability-contract.yaml`
  - canonical metric and lineage event field requirements
  - stream storage path patterns for artifact-first review
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
