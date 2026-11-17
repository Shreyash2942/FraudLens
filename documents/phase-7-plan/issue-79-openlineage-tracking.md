# Issue #79 Plan - Setup Data Lineage Tracking With OpenLineage

Issue: `#79`

Phase: `Phase 7 - Observability And Lineage`

Status date: `2026-06-17`

## Description Alignment

Map FraudLens pipeline execution, datasets, and stage transitions into OpenLineage-compatible events for traceability across ingestion, transformation, validation, and serving paths.

This issue turns the Phase 6 lineage artifact stream into OpenLineage-compatible lineage capture. It should integrate Airflow orchestration context, dbt transformation context, and governed dataset naming without losing local JSONL lineage artifacts.

## Task Breakdown

### 1. Define lineage model mapping

OpenLineage naming model:

- namespace pattern: `fraudlens.<run_profile>` or profile-specific value from orchestration settings
- job naming pattern: `fraudlens.<workflow>.<stage>` for Airflow orchestration stages
- dbt job naming pattern: `fraudlens.dbt.<layer>.<model_name>` where model-level capture is available
- run identifier: shared `pipeline_run_id` or OpenLineage run id mapped from Airflow context
- dataset naming pattern: governed FraudLens dataset name plus layer and storage context

Dataset model:

- source/generated datasets: `fraudlens.source.<dataset_name>`
- Bronze datasets: `fraudlens.bronze.<dataset_name>`
- Silver datasets: `fraudlens.silver.<entity_or_model_name>`
- Gold datasets: `fraudlens.gold.<entity_or_model_name>`
- KPI/serving datasets: `fraudlens.serving.<dashboard_or_kpi_output>`
- validation artifacts: model as quality facets or output artifacts only when they clarify pipeline behavior

Mapping work:

- map FraudLens workflows to OpenLineage jobs
- map pipeline runs to OpenLineage runs
- map generated datasets, Bronze, Silver, Gold, and KPI outputs to OpenLineage datasets
- map quality gates and validation checks to run facets where practical
- map failure category and status into run facets or event metadata
- keep event IDs and names stable across local, CI, and Snowflake profiles

### 2. Adapt existing lineage artifacts

Existing local lineage source:

- Phase 6 emits `lineage_events.jsonl` under the observability artifact path.
- Existing event types include `pipeline_run_completed`, `stage_transition`, and `quality_gate_result`.
- Required fields include event type, timestamp, namespace, job name, run id, batch id, status, inputs, and outputs.

Adapter requirements:

- define OpenLineage event payload mapping under `monitoring/openlineage/`
- preserve existing local lineage artifact output
- add namespace rules for local, CI, and Snowflake profiles
- map local event status values to OpenLineage event lifecycle semantics
- include inputs and outputs as OpenLineage datasets
- include run/profile/batch/stage context in facets or controlled metadata
- record skipped or invalid lineage events for observability metrics from issue `#76`

### 3. Configure OpenLineage integration with Airflow

Airflow integration goals:

- configure OpenLineage settings through environment variables and/or orchestration profile fields
- emit events for master pipeline stages: prepare runtime, ingestion, transformation, validation, and publish
- emit stage transition events with inputs and outputs where stage-level lineage is stable
- ensure failed delivery is logged as a warning and does not mask the original task failure
- keep Airflow task logs correlated through `pipeline_run_id`, `batch_id`, `workflow`, and `stage`

Airflow implementation boundaries:

- prefer shared helper or adapter logic over repeated DAG-specific payload construction
- keep DAG topology unchanged unless lineage context must be passed explicitly
- retain local JSONL event generation even when OpenLineage endpoint is disabled
- make endpoint delivery optional for CI and local offline use

### 4. Configure OpenLineage integration with dbt

dbt integration goals:

- capture transformation lineage across Bronze, Silver, Gold, and KPI models
- use dbt manifest/run result metadata where available to derive model inputs and outputs
- map dbt selectors and layers to governed FraudLens lineage dataset names
- include dbt model status, invocation id, selector, target, and profile context
- align dbt lineage with Airflow transformation stage events so Marquez does not show disconnected graphs

dbt implementation options:

- direct dbt OpenLineage integration if dependency and runtime support are stable
- adapter that converts dbt artifacts (`manifest.json`, `run_results.json`) into OpenLineage events
- Airflow summary mapping for transformation stage lineage as a minimum viable path

Decision preference:

- start with artifact-derived dbt lineage mapping because this repo already treats artifacts as reviewable evidence
- add direct dbt OpenLineage integration only if it does not make local development brittle

### 5. Integrate emission path

- configure OpenLineage endpoint settings through profile or environment variables
- ensure failed delivery is logged without masking pipeline failures
- include retry or deferred-delivery behavior if lightweight and deterministic
- provide a local/offline mode that only writes artifacts
- provide a live mode that sends events to the configured OpenLineage endpoint
- record delivery status for later Grafana and validation coverage

### 6. Validate lineage event generation

- validate sample OpenLineage payload structure
- validate required namespace, job, run, input, output, event time, and status fields
- validate Airflow stage lineage events from sample pipeline summaries
- validate dbt transformation lineage events from sample dbt artifacts
- validate failed or partial run lineage events
- validate malformed events are rejected or skipped with visible warnings
- verify ingestion, transformation, validation, and serving layers appear as expected
- document manual event submission test commands

### 7. Ensure transformations are captured correctly

Transformation lineage checks:

- raw/generated datasets feed Bronze outputs
- Bronze models feed Silver outputs
- Silver models feed Gold outputs
- Gold models feed KPI/serving outputs
- validation gates reference the datasets they validate
- dbt model names map back to governed dataset/model contracts
- lineage captures both successful and failed transformation runs where meaningful

Expected evidence:

- sample OpenLineage event for ingestion-to-Bronze
- sample OpenLineage event for Bronze-to-Silver transformation
- sample OpenLineage event for Silver-to-Gold transformation
- sample OpenLineage event for Gold-to-KPI serving output
- sample quality gate lineage event or facet

## Deliverables

- OpenLineage mapping contract under `monitoring/openlineage/`
- adapter or emitter implementation plan/assets
- sample OpenLineage event payloads
- Airflow OpenLineage configuration plan/assets
- dbt OpenLineage configuration or artifact-derived lineage adapter plan/assets
- tests for required lineage fields, dataset naming, and transformation edges
- documentation updates
- delivery status and troubleshooting guidance

## Implementation Plan

1. Create `monitoring/openlineage/` with namespace, job, run, dataset, and facet mapping guidance.
2. Add sample OpenLineage payloads for pipeline completion, stage transition, dbt transformation, and quality gate events.
3. Extend or add an adapter that maps local `lineage_events.jsonl` into OpenLineage-compatible payloads.
4. Add Airflow configuration hooks for OpenLineage endpoint, namespace, and enabled/disabled behavior.
5. Add dbt transformation lineage mapping from dbt artifacts or direct integration, depending on runtime stability.
6. Add validation tests for required OpenLineage fields and governed dataset naming.
7. Add transformation lineage tests that verify input/output edges across Bronze, Silver, Gold, and KPI layers.
8. Add delivery-status logging and metrics alignment for OpenLineage submission success/failure.
9. Document local/offline and live endpoint validation steps.

## Commit Plan (Issue #79)

1. `docs(openlineage): define lineage mapping contract for issue 79`
2. `feat(openlineage): add sample lineage payloads for issue 79`
3. `feat(openlineage): add artifact to openlineage adapter for issue 79`
4. `feat(airflow-lineage): configure openlineage emission controls for issue 79`
5. `feat(airflow-lineage): emit stage lineage events for issue 79`
6. `feat(dbt-lineage): map dbt artifacts to openlineage events for issue 79`
7. `test(openlineage): validate required lineage payload fields for issue 79`
8. `test(openlineage): validate governed dataset naming for issue 79`
9. `test(dbt-lineage): validate transformation input output edges for issue 79`
10. `docs(lineage): document openlineage validation workflow for issue 79`

## Acceptance Criteria Mapping

- OpenLineage integration with Airflow configured: covered by Airflow integration goals
- OpenLineage integration with dbt configured: covered by dbt integration goals and options
- lineage event generation validated: covered by payload and sample event validation
- transformations captured correctly: covered by transformation lineage checks
- lineage is captured across ingestion, transformation, validation, and serving layers
- OpenLineage payloads are profile-aware and reproducible
- local artifacts and external lineage delivery stay aligned
- failed lineage delivery is visible but non-destructive

## Risk Notes

- OpenLineage dataset naming must not drift from governed dataset contracts
- validation-only events can be over-modeled; capture enough for audit without noise
- Marquez display depends on correct namespace, job, run, input, and output mapping
- direct dbt integration can be brittle if local dependencies differ from Data-Lab runtime
- emitting both Airflow and dbt lineage can create duplicate or disconnected graphs unless naming rules are strict
- endpoint delivery must not block pipeline completion when lineage service is unavailable

## Open Decision Log

- confirm serving-layer lineage boundary before Phase 9 analytics work
- confirm OpenLineage client dependency strategy: direct client, HTTP adapter, or artifact conversion first
- confirm whether dbt lineage is emitted directly or through artifact-derived mapping
- confirm exact namespace pattern, proposed: `fraudlens.<run_profile>`
- confirm which transformation artifacts are available in local and CI runs
- confirm whether validation gates should be represented as OpenLineage jobs, facets, or metadata-only events
