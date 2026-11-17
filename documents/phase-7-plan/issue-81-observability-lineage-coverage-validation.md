# Issue #81 Plan - Validate Observability And Lineage Coverage

Issue: `#81`

Phase: `Phase 7 - Observability And Lineage`

Status date: `2026-06-17`

## Description Alignment

Validate that metrics, logs, dashboards, OpenLineage events, and Marquez visualization cover the required FraudLens pipeline paths and operational failure modes.

This issue is the Phase 7 readiness gate. It should prove that observability and lineage coverage are complete enough for production-like local operation, while clearly separating automated contract checks from live Data-Lab smoke test evidence.

## Task Breakdown

### 1. Define coverage matrix

Coverage dimensions:

- metrics
- logs
- Grafana dashboards
- local artifacts
- OpenLineage events
- Marquez visualization
- validation evidence

Pipeline coverage matrix:

| Pipeline Area | Metrics | Logs | Lineage | Dashboard | Evidence |
|---|---|---|---|---|---|
| runtime preparation | profile/run status | context resolution logs | run/job context | pipeline overview | run summary |
| ingestion | status, duration, failures | source checks and load logs | source to Bronze | pipeline and performance | metric event, lineage event |
| transformation | status, duration, dbt failures | dbt selector/build logs | Bronze to Silver to Gold to KPI | performance and failure | dbt lineage event |
| validation | gate count and failures | gate severity and failure logs | quality gate result | failure/quality | validation artifact |
| publish/artifacts | artifact completeness | publish references | final run output | pipeline overview | artifact reference |
| serving/KPI | KPI output status where available | model/output logs | Gold to serving/KPI | pipeline or lineage health | serving lineage event |

Service coverage matrix:

| Service | Monitoring Signal | Dashboard | Readiness Evidence |
|---|---|---|---|
| Airflow | availability, task/run status | system health, pipeline overview | UI/log check |
| Prometheus | scrape target health, sample query | system health | target `UP`, PromQL output |
| Grafana | datasource query and dashboard import | system health | datasource validation |
| MongoDB | artifact storage health or lookup | system health | artifact query/lookup |
| Marquez | API/UI health | lineage health | lineage graph evidence |
| Spark/Hive local runtime | health probe or documented availability | system health | runtime check |

### 2. Add automated checks

- validate metric contract completeness
- validate Prometheus mapping assets
- validate Grafana dashboard JSON assets
- validate OpenLineage sample payloads
- validate required documentation references
- validate logging metadata and redaction expectations from issue `#78`
- validate coverage matrix rows link to concrete assets or evidence placeholders
- validate no required Phase 7 workstream lacks a validation entry

Recommended automated checks:

- `test_phase7_metric_contract_completeness`
- `test_phase7_prometheus_mapping_assets`
- `test_phase7_grafana_dashboard_assets`
- `test_phase7_logging_visibility_contract`
- `test_phase7_openlineage_payload_samples`
- `test_phase7_marquez_validation_plan`
- `test_phase7_coverage_matrix_references`

### 3. Add manual smoke test evidence

- local pipeline run observability artifact inspection
- Prometheus target or sample scrape evidence
- Grafana dashboard import or provisioning evidence
- Marquez lineage visualization evidence
- Airflow UI task log evidence
- OpenLineage event delivery or offline payload generation evidence
- ingestion to transformation to serving lineage path evidence

Manual smoke test sequence:

1. run or inspect a representative local pipeline execution
2. confirm Airflow task logs are accessible for each critical stage
3. confirm metric events are emitted locally
4. confirm Prometheus target health and sample query output
5. confirm Grafana datasource and dashboard panels load
6. confirm OpenLineage payloads are generated for stage and transformation events
7. confirm Marquez displays lineage when live endpoint is available
8. confirm run artifacts, metric events, logs, and lineage events share correlation identifiers

Evidence artifacts:

- `documents/validation/phase-7-observability-lineage-coverage.md`
- optional JSON evidence manifest for commands, timestamps, and asset paths
- optional screenshots under `documents/assets/` only if required for Grafana or Marquez closeout

### 4. Validate monitoring coverage across services

Monitoring coverage checks:

- all mandatory services have a target, probe, or documented limitation
- Prometheus includes FraudLens pipeline metrics and service health signals
- Grafana visualizes pipeline status, task duration, failures, and service health
- metric storage is confirmed with fresh PromQL query output
- missing optional exporters are explicitly listed as gaps or future work

Mandatory monitoring coverage:

- FraudLens pipeline run status
- pipeline/stage duration
- task failures and retries
- artifact completeness
- quality gate outcomes
- Airflow availability or log access
- Prometheus health
- Grafana datasource health
- Marquez health for lineage visualization

### 5. Validate lineage across ingestion to transformation to serving

Lineage path checks:

- source/generated dataset to Bronze output
- Bronze output to Silver model/output
- Silver output to Gold model/output
- Gold output to KPI/serving output
- validation gate result associated with validated dataset or stage
- pipeline completion event references final outputs

Lineage validation modes:

- contract mode: validate sample OpenLineage payloads and local JSONL artifacts
- local runtime mode: submit events to configured OpenLineage/Marquez endpoint when available
- visual mode: confirm Marquez shows expected job/run/dataset path

### 6. Identify gaps

- identify must-fix gaps before final documentation
- classify optional follow-ups for later analytics or CI/CD phases
- publish validation evidence in `documents/validation/` or this Phase 7 folder

Gap classification:

- `blocker`: breaks core Phase 7 definition of done
- `must_fix`: required before final Phase 7 handoff
- `accepted_limitation`: documented runtime limitation for local/CI
- `follow_up`: appropriate for Phase 8, Phase 9, or future hardening

Gap register fields:

- gap id
- affected workstream
- severity
- evidence
- remediation owner/file
- target issue or follow-up phase
- readiness impact

### 7. Confirm readiness for production-like use

Readiness criteria:

- metrics cover pipeline execution and service health
- Grafana dashboards provide actionable operational views
- logs are accessible and can explain failures
- OpenLineage captures critical dataset movement
- Marquez can visualize lineage when endpoint is available
- coverage gaps are classified and documented
- local reproducibility remains available without Snowflake
- final documentation has evidence-backed status

Readiness decision values:

- `READY`: all required checks pass
- `READY_WITH_LIMITATIONS`: core checks pass with documented local/runtime limitations
- `NOT_READY`: one or more blockers remain

## Deliverables

- coverage matrix document
- validation script or tests where practical
- manual smoke test checklist
- readiness notes for final Phase 7 handoff
- gap register
- production-like readiness decision
- validation evidence manifest

## Implementation Plan

1. Create the Phase 7 coverage matrix covering pipeline areas, services, and evidence types.
2. Add automated validation checks for metrics, Prometheus, Grafana, logging, OpenLineage, and Marquez assets.
3. Add lineage path validation for ingestion to transformation to serving/KPI outputs.
4. Add manual smoke test checklist for Airflow, Prometheus, Grafana, OpenLineage, and Marquez.
5. Add gap register format and classify any missing coverage.
6. Add readiness decision document with `READY`, `READY_WITH_LIMITATIONS`, or `NOT_READY` outcome.
7. Update final documentation inputs for issue `#82`.

## Commit Plan (Issue #81)

1. `docs(validation): define phase 7 coverage matrix for issue 81`
2. `test(validation): validate phase 7 metric coverage for issue 81`
3. `test(validation): validate grafana dashboard coverage for issue 81`
4. `test(validation): validate logging visibility coverage for issue 81`
5. `test(validation): validate openlineage payload coverage for issue 81`
6. `test(validation): validate lineage path coverage for issue 81`
7. `docs(validation): add phase 7 smoke test checklist for issue 81`
8. `docs(validation): add observability lineage gap register for issue 81`
9. `docs(validation): publish phase 7 readiness decision for issue 81`
10. `docs(observability): link validation evidence for issue 81`

## Acceptance Criteria Mapping

- monitoring coverage across services validated: covered by service coverage matrix and monitoring checks
- lineage across ingestion to transformation to serving validated: covered by lineage path checks
- gaps identified: covered by gap classification and gap register
- production-like readiness confirmed: covered by readiness criteria and decision values
- metrics are collected for pipeline execution and system health
- logs are useful for debugging
- dashboards show required operational views
- lineage is captured and visualized end to end
- documentation has evidence-backed validation status

## Risk Notes

- dashboard validation can appear complete even when metric data is sparse
- CI may only validate contracts, not live service integrations
- lineage coverage should be judged by governed pipeline boundaries, not by every implementation detail
- readiness can be overstated if live-service evidence is missing; clearly separate contract and runtime checks
- Marquez validation depends on issue `#80` availability and local Data-Lab service health
- serving coverage may remain KPI-output focused until Phase 9 analytics dashboards mature

## Open Decision Log

- confirm exact evidence folder for Phase 7 validation artifacts, proposed `documents/validation/`
- confirm minimum live-service checks required before closeout
- confirm whether failed-run evidence is required in addition to success-run evidence
- confirm whether `READY_WITH_LIMITATIONS` is acceptable when CI only validates contracts
- confirm whether screenshots are mandatory for Grafana and Marquez validation
