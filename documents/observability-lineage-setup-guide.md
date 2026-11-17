# Observability and Lineage Setup Guide

Issue: #82 — Document Observability & Lineage Setup  
Phase: 7 — Observability & Lineage

## Purpose

This guide explains how to use the FraudLens observability and lineage layer after Phase 7.

## Components

| Component | Role | Location |
| --- | --- | --- |
| Airflow | Orchestrates pipeline runs, structured logs, and artifacts. | `airflow/` |
| Prometheus | Scrapes and stores metrics. | `monitoring/prometheus/` |
| Grafana | Visualizes pipeline, system, failure, and lineage health. | `monitoring/grafana/` |
| OpenLineage | Defines lineage event payloads. | `documents/openlineage-tracking-contract.md` |
| Marquez | Displays lineage graph and run history. | `monitoring/marquez/` |
| Coverage validation | Confirms observability and lineage readiness. | `monitoring/coverage/` |

## Setup Order

1. Configure Airflow orchestration profiles.
2. Generate or run a pipeline workflow.
3. Confirm structured logs and local artifacts are emitted.
4. Render Prometheus metrics from metric JSONL artifacts.
5. Provision Grafana datasource and dashboards.
6. Validate OpenLineage-compatible JSONL events.
7. Dry-run Marquez delivery.
8. Confirm Marquez UI lineage when the service is available.
9. Run coverage validation.

## Core Validation Commands

```powershell
py monitoring\prometheus\render_fraudlens_metrics.py monitoring\prometheus\sample-metric-events.jsonl
py scripts\validate_observability_lineage_coverage.py
py -m pytest tests\test_phase7_coverage_matrix.py -q
```

## Documentation Map

- Metrics strategy: `monitoring/metrics-catalog.md`
- Alert guidance: `monitoring/alert-thresholds.md`
- Prometheus setup: `monitoring/prometheus/README.md`
- Grafana setup: `monitoring/grafana/README.md`
- Logging visibility: `documents/airflow-logging-visibility-contract.md`
- OpenLineage setup: `documents/openlineage-airflow-dbt-runbook.md`
- Marquez setup: `documents/marquez-lineage-visualization-runbook.md`
- Coverage readiness: `documents/observability-lineage-coverage-readiness-report.md`
