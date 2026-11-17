# Lineage Interpretation Guide

Issue: #82 — Document Observability & Lineage Setup  
Phase: 7 — Observability & Lineage

## Purpose

Use this guide to interpret FraudLens lineage events and Marquez lineage graphs.

## Event Locations

Local lineage evidence is written to:

```text
airflow/artifacts/observability/lineage/<workflow>/<run_stamp>/lineage_events.jsonl
```

Each record includes:

- FraudLens correlation fields
- OpenLineage-compatible `openlineage_event`
- input datasets
- output datasets
- run and job facets

## Key Fields

| Field | Meaning |
| --- | --- |
| `event_type` | FraudLens event category. |
| `job_name` | Airflow DAG or dbt model job. |
| `run_id` | Pipeline or dbt run identifier. |
| `batch_id` | Synthetic data batch under analysis. |
| `inputs` | Upstream datasets or artifacts. |
| `outputs` | Downstream datasets or artifacts. |
| `openlineage_event.eventType` | OpenLineage lifecycle status. |
| `openlineage_event.job.namespace` | Runtime lineage namespace. |

## Layer Interpretation

| Layer | What to Look For |
| --- | --- |
| Ingestion | Batch input datasets and Bronze-stage outputs. |
| Transformation | dbt model dependencies from manifest metadata. |
| Serving | Gold facts, dimensions, and KPI model outputs. |
| Visualization | Marquez jobs, runs, datasets, and facets. |

## Marquez Interpretation

In Marquez:

1. open the FraudLens namespace
2. select an Airflow or dbt job
3. confirm the run ID matches the delivered event
4. inspect upstream input datasets
5. inspect downstream output datasets
6. review run facets for `pipeline_run_id`, `batch_id`, and `run_profile`

## Common Questions

### Why does Marquez show a job but no downstream dataset?

The delivered OpenLineage event likely has an empty `outputs` list. Inspect the local JSONL event before delivery.

### Why does a dbt model have unexpected upstream inputs?

The exporter derives inputs from `manifest.json` `depends_on.nodes`. Re-run `dbt parse` or `dbt compile` to refresh the manifest.

### Why are namespaces split?

Namespaces follow runtime profiles such as `fraudlens.orchestration.local` and `fraudlens.orchestration.ci`.
