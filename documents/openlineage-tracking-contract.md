# OpenLineage Tracking Contract

Issue: #79 — Setup Data Lineage Tracking (OpenLineage)  
Phase: 7 — Observability & Lineage

## Purpose

FraudLens lineage events must be emitted in a shape that can be inspected locally and delivered to Marquez through the OpenLineage ingestion API. The local event stream remains the source of truth for deterministic tests and offline validation.

## Scope

Lineage capture covers:

- ingestion input batches and Bronze staging outputs
- dbt transformation stages from Bronze to Silver, Gold, and KPI models
- pipeline summary artifacts produced by Airflow orchestration
- serving-layer outputs represented by Gold facts, dimensions, and KPI models

## Event Shape

Each local lineage record must keep the existing FraudLens fields and include an `openlineage_event` object.

Required FraudLens envelope fields:

| Field | Purpose |
| --- | --- |
| `event_type` | FraudLens event category such as `pipeline_run_completed` or `dbt_transformation_completed`. |
| `event_time_utc` | UTC event timestamp. |
| `namespace` | FraudLens lineage namespace for the selected runtime profile. |
| `job_name` | Stable Airflow or dbt job name. |
| `run_id` | Run identifier shared with logs and metrics. |
| `batch_id` | Data batch associated with the event. |
| `run_profile` | Runtime profile such as `local`, `ci`, or `snowflake`. |
| `status` | Event outcome such as `SUCCESS`, `FAILED`, or `PARTIAL`. |
| `inputs` | Input dataset references. |
| `outputs` | Output dataset references. |
| `openlineage_event` | OpenLineage-compatible event payload. |

Required OpenLineage payload fields:

| Field | Purpose |
| --- | --- |
| `eventType` | OpenLineage event type, mapped from FraudLens status. |
| `eventTime` | UTC event timestamp. |
| `producer` | FraudLens producer URI. |
| `run.runId` | Deterministic UUIDv5 derived from namespace, job name, and pipeline execution ID. Stable across updates of that job execution; distinct across models. |
| `run.facets.fraudlens_run` | FraudLens run metadata. |
| `job.namespace` | OpenLineage namespace. |
| `job.name` | Stable job name. |
| `inputs[]` | Input datasets with namespace and name. |
| `outputs[]` | Output datasets with namespace and name. |

## Status Mapping

The original pipeline execution ID remains in `run.facets.fraudlens_run.pipeline_run_id` and the envelope `run_id`. This preserves log and metric correlation while satisfying the [OpenLineage run identity contract](https://openlineage.io/docs/spec/object-model/).

| FraudLens Status | OpenLineage `eventType` |
| --- | --- |
| `SUCCESS` | `COMPLETE` |
| `FAILED` | `FAIL` |
| `PARTIAL` | `OTHER` |
| active or unknown | `OTHER` |

## Dataset Naming

Dataset names should be repository-relative paths, dbt unique IDs, or stable logical relation names. Dataset namespaces should come from the profile lineage namespace unless a source explicitly provides one.

## dbt Integration

dbt lineage must be derived from dbt manifest dependencies when available. A dbt model event should include:

- model unique ID as the job name suffix
- upstream sources and models as inputs
- the materialized model relation as output
- dbt package, resource type, materialization, and layer metadata in facets

## Acceptance Checklist

- Airflow emits OpenLineage-compatible payloads for pipeline completion events.
- dbt transformation lineage can be generated from manifest metadata.
- Local lineage JSONL records preserve FraudLens correlation keys.
- OpenLineage payloads contain inputs, outputs, run facets, and job facets.
- Tests validate event generation without requiring a running Marquez service.
