# Phase 7 Plan Workspace

This folder contains planning artifacts for Phase 7 (Observability And Lineage).

## Scope

- milestone: Phase 7 Observability And Lineage
- branch: `observability-lineage`
- main outcome: a fully observable data platform with metrics, dashboards, logs, lineage capture, and lineage visualization
- sub-issues: `#75` to `#82`

## Phase Objectives

- enable system and pipeline monitoring
- track execution metrics and pipeline performance
- implement centralized dashboards
- capture data lineage across ingestion, transformation, validation, and serving layers
- improve debugging and operational visibility
- support governance, audit, and reproducibility requirements

## Workstream Order

| Order | Issue | Plan File | Purpose |
|---|---|---|---|
| 1 | `#75` | `issue-75-observability-strategy-metrics.md` | define metric taxonomy, SLOs, labels, and alerting intent |
| 2 | `#76` | `issue-76-prometheus-metrics-collection.md` | expose and collect metrics through Prometheus-compatible assets |
| 3 | `#77` | `issue-77-grafana-monitoring-dashboards.md` | build dashboards for pipeline health and platform visibility |
| 4 | `#78` | `issue-78-pipeline-logging-visibility.md` | standardize log access, run visibility, and debug workflows |
| 5 | `#79` | `issue-79-openlineage-tracking.md` | map FraudLens run events into OpenLineage-compatible events |
| 6 | `#80` | `issue-80-marquez-lineage-visualization.md` | configure Marquez ingestion and lineage UI validation |
| 7 | `#81` | `issue-81-observability-lineage-coverage-validation.md` | validate coverage across metrics, logs, dashboards, and lineage |
| 8 | `#82` | `issue-82-observability-lineage-documentation.md` | consolidate setup, runbooks, evidence, and final handoff |

## Existing Phase 6 Starting Point

Phase 6 already established the first observability layer:

- `airflow/config/orchestration_profiles.yml` has per-profile `observability` blocks.
- `airflow/dags/_fraudlens_orchestration_common.py` emits metric and lineage artifacts.
- `airflow/artifacts/observability/metrics/<workflow>/<run_stamp>/metric_events.jsonl` is the local metric stream pattern.
- `airflow/artifacts/observability/lineage/<workflow>/<run_stamp>/lineage_events.jsonl` is the local lineage stream pattern.
- `monitoring/observability-contract.yaml` defines the first metric and lineage event contract.
- `documents/airflow-observability-lineage-design.md` and `documents/airflow-observability-operations-runbook.md` provide the Phase 6 support docs.

Phase 7 should extend this artifact-first foundation into service-integrated observability without breaking local reproducibility.

## Phase 7 Implementation Strategy

1. Treat the existing JSONL event artifacts as the canonical local source of truth.
2. Add Prometheus/Grafana integration as adapters and dashboard assets under `monitoring/`.
3. Add OpenLineage/Marquez integration as event mapping and delivery layers, not as a replacement for local artifacts.
4. Keep local, CI, and future Snowflake profiles explicit in configuration.
5. Validate every integration with deterministic checks and documented evidence.
6. Consolidate final outcomes into a new top-level Phase 7 handoff document after sub-issue completion.

## Final Documentation

This folder preserves the original implementation plans. Final outcomes are consolidated in:

- `documents/phase-7-observability-lineage.md`

The final handoff summarizes setup, dashboards, lineage flow, validation evidence, and operations guidance. Refer to it for delivery status; the plans below retain historical proposals and decisions.
