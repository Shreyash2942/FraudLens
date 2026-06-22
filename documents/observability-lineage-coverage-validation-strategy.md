# Observability and Lineage Coverage Validation Strategy

Issue: #81 — Validate Observability & Lineage Coverage  
Phase: 7 — Observability & Lineage

## Purpose

Validate that FraudLens has usable monitoring, logging, dashboard, and lineage coverage across the critical pipeline path from ingestion through transformation and serving.

## Coverage Dimensions

Coverage is evaluated across four dimensions:

| Dimension | Validation Goal |
| --- | --- |
| Metrics | Each critical workflow emits or maps to Prometheus-ready metrics. |
| Dashboards | Operational dashboards expose pipeline, system, failure, and lineage status. |
| Logs | Airflow task logs carry structured context for debugging and artifact lookup. |
| Lineage | OpenLineage-compatible events describe inputs, transformations, and outputs. |

## Critical Flow

The validation target is the production-like data flow:

```text
synthetic batch
  -> ingestion workflow
  -> Bronze staging
  -> dbt transformation
  -> Silver models
  -> Gold facts/dimensions
  -> KPI/serving models
  -> dashboards and lineage visualization
```

## Service Coverage

The platform must include validation evidence for:

- Airflow orchestration and task logs
- Prometheus scrape and metric conversion assets
- Grafana dashboard provisioning and dashboards
- OpenLineage event generation
- Marquez health, delivery, and UI validation assets
- MongoDB/local artifact persistence settings where applicable

## Gap Classification

| Status | Meaning |
| --- | --- |
| `covered` | Validation assets and docs are present. |
| `partial` | Some evidence exists, but manual validation remains. |
| `planned` | Scope is recognized for future hardening. |
| `blocked` | Validation cannot proceed without external service availability. |

## Acceptance Checklist

- Coverage matrix exists and includes all critical services.
- Lineage path covers ingestion, transformation, and serving layers.
- Validation tests confirm required assets are present.
- Known gaps are documented with owner-friendly next actions.
- Production-like readiness criteria are explicitly stated.
