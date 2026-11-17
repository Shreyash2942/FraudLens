# Issue #76 Plan - Implement Metrics Collection With Prometheus

Issue: `#76`  
Phase: `Phase 7 - Observability And Lineage`  
Status date: `2026-06-17`

## Description Alignment

Expose FraudLens pipeline and service metrics in a Prometheus-compatible form while preserving the existing artifact-first observability contract.

This issue turns the strategy from issue `#75` into a concrete Prometheus collection path. It configures scrape targets, connects Airflow/platform endpoints, validates collection, and documents how operators prove that metrics are being retained.

## Task Breakdown

### 1. Choose collection pattern

Recommended collection model:

- keep JSONL metric artifacts as the canonical local run evidence
- add a lightweight FraudLens metrics adapter for Prometheus ingestion
- keep exporter configuration under `monitoring/` rather than embedding Prometheus concerns directly inside DAG business logic
- use profile-aware settings for `local`, `ci`, and future `snowflake`
- treat Data-Lab Prometheus as the local runtime collector

Pattern decision:

- preferred first implementation: artifact-to-Prometheus adapter reading canonical metric events
- acceptable local fallback: generated Prometheus textfile metrics for node/textfile collector style collection
- deferred unless already available in Data-Lab: Airflow StatsD bridge and external exporter sidecars

### 2. Implement metric adapter assets

Adapter requirements:

- map canonical JSONL metrics into `fraudlens_` Prometheus metric names
- normalize labels using the issue `#75` cardinality rules
- expose or generate metrics for pipeline run status, duration, stage status, stage duration, task attempts, failures, artifact completeness, quality gate outcomes, and lineage event counts
- include sample metric event inputs and expected Prometheus exposition outputs
- handle missing artifact directories without failing the primary pipeline
- skip malformed metric records with warning counters instead of crashing the adapter
- expose adapter self-health metrics such as parsed event count and skipped event count

### 3. Add Prometheus configuration

Configuration assets:

- add Prometheus scrape config under `monitoring/prometheus/`
- include a FraudLens metrics adapter job
- include Airflow webserver or scheduler health target if exposed by Data-Lab
- include Marquez health target if available for later lineage validation
- include MongoDB exporter or documented MongoDB artifact storage health target if available
- include Spark/Hive runtime health targets where practical
- keep target hostnames and ports documented as Data-Lab integration values, not hard-coded guarantees

### 4. Add Airflow and service endpoints

- document how Airflow metrics or health endpoints are reached in Data-Lab
- add scrape configuration only for endpoints that are stable in the local runtime
- ensure DAG-level FraudLens metrics remain separate from generic Airflow service metrics
- document Prometheus, Grafana, Marquez, MongoDB, Spark, and Hive endpoint assumptions
- keep CI validation contract-based when live services are unavailable

### 5. Validate metric collection

- test metric mapping from sample JSONL payloads to Prometheus exposition format
- validate metric names use the `fraudlens_` prefix
- validate required labels exist and blocked labels do not appear
- validate Prometheus scrape configuration syntax
- validate sample storage/query evidence templates exist

### 6. Ensure metric storage is working

- confirm Prometheus target status shows recent scrape timestamps
- confirm sample metric queries return values across at least one scrape interval
- confirm Prometheus local storage path is documented for Data-Lab
- confirm retention expectations are documented as local runtime configuration
- document how to distinguish missing source events from failed Prometheus storage

## Deliverables

- Prometheus scrape configuration under `monitoring/prometheus/`
- FraudLens metric mapping and adapter assets under `monitoring/prometheus/`
- sample metric payloads and expected exposition fixtures
- tests for metric conversion and scrape config
- updated monitoring README and standards references
- metrics collection runbook section
- validation evidence checklist for Prometheus target health and sample storage

## Implementation Plan

1. Create `monitoring/prometheus/` with scrape configuration conventions and target placeholders.
2. Add FraudLens metric adapter assets that convert canonical JSONL metric events to Prometheus-readable metrics.
3. Add sample metric events and expected Prometheus exposition output.
4. Add Airflow and platform service scrape target documentation for Data-Lab.
5. Add validation checks for config shape, metric naming, labels, and sample conversion.
6. Add storage verification guidance using target health and sample PromQL queries.
7. Update monitoring docs to make Prometheus setup discoverable.

## Commit Plan (Issue #76)

1. `docs(prometheus): define metrics collection architecture for issue 76`
2. `feat(monitoring): add prometheus scrape configuration for issue 76`
3. `feat(monitoring): add fraudlens metric adapter contract for issue 76`
4. `feat(monitoring): add airflow and service scrape targets for issue 76`
5. `test(monitoring): validate prometheus metric mapping for issue 76`
6. `test(monitoring): validate prometheus scrape config for issue 76`
7. `docs(prometheus): document metric storage verification for issue 76`
8. `docs(monitoring): update prometheus runbook references for issue 76`

## Acceptance Criteria Mapping

- Prometheus scrape targets configured: covered by scrape configuration assets
- Airflow and service endpoints added: covered by Airflow and service endpoint work
- metrics collection validated: covered by automated and manual validation sections
- metric storage verified: covered by Prometheus target and query evidence
- pipeline execution and system health metrics are Prometheus-readable
- metric names and labels match the Phase 7 strategy
- collection works locally without requiring Snowflake
- failures in metric export do not hide primary pipeline failures

## Risk Notes

- direct Airflow metrics may differ from FraudLens run metadata unless labels are normalized
- scrape endpoints can create runtime coupling if the adapter must always be online
- Data-Lab service ports may differ by local environment; keep them documented and configurable
- Prometheus storage validation can pass with old samples unless queries check freshness
- optional service targets should not make the primary FraudLens metrics target look broken

## Open Decision Log

- confirm preferred Data-Lab Prometheus integration path: adapter endpoint or textfile collector
- confirm exact Airflow metrics or health endpoint exposed by Data-Lab
- confirm whether adapter code lives in `monitoring/` or `airflow/`
- confirm which service targets are mandatory for issue `#76` versus planned for later validation
- confirm retention and cleanup expectations for generated metric files
