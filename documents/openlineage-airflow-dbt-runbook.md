# OpenLineage Airflow and dbt Runbook

Issue: #79 — Setup Data Lineage Tracking (OpenLineage)  
Phase: 7 — Observability & Lineage

## Purpose

Use this runbook to validate FraudLens OpenLineage event generation without requiring a live Marquez service.

## Configuration

OpenLineage settings live under each profile in `airflow/config/orchestration_profiles.yml`:

- `openlineage_enabled`
- `openlineage_transport`
- `openlineage_url_env`
- `openlineage_default_url`
- `openlineage_producer`

Container-local delivery defaults to `OPENLINEAGE_URL=http://localhost:5000/api/v1/lineage`. On the Windows host, the current `fraudlens` container maps this to `http://127.0.0.1:5002/api/v1/lineage`; confirm with `docker port fraudlens`.

OpenLineage `run.runId` is a deterministic UUID scoped to namespace, job, and pipeline execution. The original Airflow/dbt ID remains in the local envelope and `run.facets.fraudlens_run.pipeline_run_id`. Each model receives its own UUID so Marquez keeps model inputs and outputs separate.

## Airflow Lineage Events

Airflow emits lineage through `emit_lineage_event` in `airflow/dags/_fraudlens_orchestration_common.py`.

Generated local stream:

```powershell
airflow\artifacts\observability\lineage\<workflow>\<run_stamp>\lineage_events.jsonl
```

Each record includes:

- FraudLens envelope fields for log and metric correlation
- `openlineage_schema_version`
- nested `openlineage_event` payload for delivery to Marquez or another OpenLineage receiver

## dbt Lineage Export

Export dbt manifest dependencies into OpenLineage-compatible JSONL:

```powershell
py dbt\scripts\export_openlineage_from_manifest.py `
  --manifest dbt\target\manifest.json `
  --output airflow\artifacts\observability\lineage\transformation\manual\dbt_openlineage_events.jsonl `
  --namespace fraudlens.orchestration.local `
  --run-id manual-dbt-run `
  --batch-id <batch_id>
```

The exporter maps:

- dbt source/model dependencies to OpenLineage inputs
- dbt model relations to OpenLineage outputs
- dbt layer, resource type, package, and materialization into facets

## Validation

Run focused tests:

```powershell
py -m pytest airflow\tests\test_openlineage_integration.py tests\test_phase7_dbt_openlineage_export.py -q
```

Inspect generated local events:

```powershell
Get-Content airflow\artifacts\observability\lineage\<workflow>\<run_stamp>\lineage_events.jsonl -Tail 5
```

Validate these fields:

- `event_type`
- `job_name`
- `run_id`
- `batch_id`
- `inputs`
- `outputs`
- `openlineage_event.eventType`
- `openlineage_event.run.runId`
- `openlineage_event.job.namespace`

## Handoff to Marquez

Issue #80 provides Marquez delivery and visualization assets. Keep the local JSONL stream as evidence even when delivery to Marquez is enabled.
