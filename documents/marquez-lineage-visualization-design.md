# Marquez Lineage Visualization Design

Issue: #80 — Integrate Lineage Visualization (Marquez)  
Phase: 7 — Observability & Lineage

## Purpose

Marquez provides the lineage UI and API layer for OpenLineage events emitted by FraudLens Airflow and dbt workflows.

## Integration Model

FraudLens keeps local lineage JSONL files as deterministic evidence, then delivers nested `openlineage_event` payloads to Marquez when the service is available.

```text
Airflow/dbt lineage events
  -> airflow/artifacts/observability/lineage/<workflow>/<run_stamp>/lineage_events.jsonl
  -> OpenLineage payload extraction
  -> Marquez OpenLineage ingestion API
  -> Marquez UI lineage graph
```

## Marquez Endpoints

| Variable | Default | Purpose |
| --- | --- | --- |
| `MARQUEZ_BASE_URL` | `http://localhost:5000` | Marquez API base URL for health checks. |
| `MARQUEZ_UI_URL` | `http://localhost:3000` | Marquez web UI. |
| `OPENLINEAGE_URL` | `http://localhost:5000/api/v1/lineage` | Full OpenLineage ingestion endpoint for event delivery. |

## Visualization Expectations

Marquez should show:

- Airflow pipeline job lineage for pipeline completion events
- dbt transformation job lineage for model dependency events
- input batch datasets
- Bronze, Silver, Gold, and KPI transformation outputs
- run-level facets containing `pipeline_run_id`, `batch_id`, and `run_profile`

## Validation Strategy

Validation is split into offline and live checks:

1. offline tests validate Marquez config and OpenLineage payload extraction
2. health helper checks whether Marquez API is reachable
3. delivery helper posts OpenLineage payloads when `OPENLINEAGE_URL` is configured
4. operator confirms lineage appears correctly in the Marquez UI

## Acceptance Checklist

- Marquez configuration is documented.
- OpenLineage JSONL events can be converted to delivery payloads.
- Delivery helper supports dry-run validation.
- Health helper records Marquez API status.
- UI validation workflow is documented for operators.
