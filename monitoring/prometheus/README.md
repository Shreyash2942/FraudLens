# Prometheus Metrics Collection

Issue: `#76`  
Phase: `Phase 7 - Observability And Lineage`

This folder contains Prometheus-facing assets for collecting FraudLens pipeline and service metrics.

## Collection Architecture

FraudLens keeps local JSONL metric artifacts as the canonical audit source and exposes Prometheus-compatible metrics through an adapter layer.

Collection path:

1. Airflow emits local metric events under `airflow/artifacts/observability/metrics/<workflow>/<run_stamp>/metric_events.jsonl`.
2. The FraudLens Prometheus adapter reads those canonical events.
3. The adapter renders Prometheus exposition text with `fraudlens_` metric names.
4. Prometheus scrapes the adapter endpoint or a configured textfile collector path.
5. Grafana uses Prometheus as its primary datasource.

## Local Runtime Assumptions

- Data-Lab is the expected local runtime for Prometheus.
- Snowflake remains the future analytics target and is not required for local metric collection.
- Local and CI runs may validate mapping and scrape configuration without live service endpoints.
- Live service target health depends on which Data-Lab endpoints are exposed locally.

## Files

- `prometheus.yml`: local scrape configuration for FraudLens and related service targets.
- `fraudlens_metrics_mapping.yaml`: mapping contract from local JSONL events to Prometheus metrics.
- `render_fraudlens_metrics.py`: local adapter utility that renders Prometheus exposition text from metric artifacts.
- `sample-metric-events.jsonl`: deterministic input events for validation.
- `expected-fraudlens-metrics.prom`: expected exposition output for sample events.
- `storage-verification.md`: operator checks for confirming Prometheus target health and sample retention.

## Validation Modes

- contract validation: parse static mapping, samples, and scrape config
- adapter validation: render sample metric events into exposition output
- local runtime validation: confirm Prometheus targets are `UP` and queries return fresh samples

