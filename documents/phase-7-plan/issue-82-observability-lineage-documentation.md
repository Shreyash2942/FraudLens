# Issue #82 Plan - Document Observability And Lineage Setup

Issue: `#82`

Phase: `Phase 7 - Observability And Lineage`

Status date: `2026-06-17`

## Description Alignment

Consolidate Phase 7 implementation, setup steps, operational runbooks, validation evidence, and handoff guidance into complete observability and lineage documentation.

This issue is the final Phase 7 documentation workstream. It should make monitoring dashboards, metrics, logs, OpenLineage events, and Marquez lineage usable by someone operating the project from the repository and the local Data-Lab runtime.

## Task Breakdown

### 1. Consolidate final architecture

- summarize metric collection architecture
- summarize dashboard architecture
- summarize logging and artifact visibility
- summarize OpenLineage and Marquez lineage flow
- explain local Data-Lab role and future Snowflake direction

Final architecture sections:

- Phase 7 objective and scope
- runtime topology: Airflow, Prometheus, Grafana, OpenLineage, Marquez, MongoDB artifact store, Spark/Hive surrogate runtime
- artifact-first design: local JSONL metric and lineage events remain canonical review evidence
- metrics flow: Airflow/run artifacts to Prometheus-compatible collection to Grafana dashboards
- logging flow: Airflow UI logs plus run artifacts and MongoDB artifact records
- lineage flow: Airflow/dbt context to local lineage artifacts to OpenLineage payloads to Marquez visualization
- profile model: `local`, `ci`, and `snowflake` behavior
- validation model: automated contract checks plus live Data-Lab smoke tests

### 2. Document metrics and dashboards

Metrics documentation:

- metric strategy and naming convention from issue `#75`
- Prometheus collection setup from issue `#76`
- scrape targets and service endpoint expectations
- sample PromQL queries for run status, durations, failures, quality gates, and service health
- metric storage/freshness verification steps
- known metric limitations and optional targets

Dashboard documentation:

- Grafana datasource setup from issue `#77`
- dashboard import or provisioning steps
- dashboard catalog and intended operator use:
  - pipeline overview
  - pipeline performance
  - failure and quality
  - system health
  - lineage health
- dashboard variable guidance for profile, workflow, stage, service, and status
- expected dashboard validation evidence

### 3. Document lineage setup and interpretation

OpenLineage setup:

- endpoint and namespace configuration
- local/offline artifact mode
- live delivery mode
- Airflow integration behavior
- dbt integration or artifact-derived mapping behavior
- required environment variables and profile controls

Marquez setup:

- health/API endpoint expectations
- event delivery dependency on OpenLineage payloads
- UI validation steps
- replay or re-run guidance if supported

Lineage interpretation:

- how to read jobs, runs, inputs, and outputs
- how to trace source/generated datasets to Bronze, Silver, Gold, and KPI/serving outputs
- how validation gates appear in lineage
- how to identify disconnected or missing lineage paths
- how to correlate Marquez lineage with Airflow logs and run artifacts

### 4. Publish setup documentation

- Prometheus configuration and validation steps
- Grafana datasource/dashboard provisioning steps
- OpenLineage endpoint configuration
- Marquez health and UI validation steps
- profile/environment variable reference
- Data-Lab service assumptions and local fallback behavior
- CI contract-validation boundaries

### 5. Add troubleshooting guidelines

- daily/normal run observability checks
- failure triage workflow
- metric and log correlation workflow
- lineage delivery and Marquez troubleshooting
- evidence capture requirements

Troubleshooting sections:

- no metric events emitted
- Prometheus target down
- metric query returns no data
- Grafana datasource fails
- dashboard panels are empty
- Airflow logs missing expected context
- MongoDB artifact lookup fails
- OpenLineage payload generation fails
- OpenLineage delivery fails
- Marquez does not show expected lineage
- transformation lineage is incomplete or disconnected
- validation coverage is `READY_WITH_LIMITATIONS`

### 6. Publish operations runbook

- normal run monitoring checklist
- failed run triage checklist
- evidence capture checklist
- dashboard interpretation checklist
- lineage interpretation checklist
- service health checklist
- escalation path from symptom to likely source

### 7. Update README and docs

- update `documents/README.md`
- update `monitoring/README.md`
- update `monitoring/STANDARDS.md`
- update `airflow/README.md` if final docs supersede Phase 6 support references
- link final Phase 7 handoff from related Airflow and platform docs if needed
- record known limitations and follow-up items

Index expectations:

- `documents/README.md` phase map includes `observability-lineage.md` as Phase 7 final handoff
- `documents/phase-7-plan/README.md` links final outcome after completion
- `monitoring/README.md` links Prometheus, Grafana, OpenLineage, and Marquez assets
- final handoff links validation evidence from issue `#81`
- final handoff explains remaining accepted limitations and follow-up phases

### 8. Capture final handoff evidence

Evidence sections:

- implementation summary by issue `#75` to `#82`
- commit ledger or summary, matching the Phase 6 handoff style if appropriate
- validation status and readiness decision from issue `#81`
- asset inventory for monitoring, dashboards, lineage, tests, and runbooks
- known limitations and next-phase follow-ups

## Deliverables

- `documents/observability-lineage.md`
- updated monitoring README/runbook references
- final validation evidence links
- completed Phase 7 planning folder
- updated `documents/README.md`
- updated `monitoring/README.md`
- updated `monitoring/STANDARDS.md`
- optional update to `airflow/README.md`
- final setup and troubleshooting runbook content

## Implementation Plan

1. Draft `documents/observability-lineage.md` with architecture, setup, usage, troubleshooting, validation, and handoff sections.
2. Add metrics and dashboard documentation based on issues `#75`, `#76`, and `#77`.
3. Add logging and debugging documentation based on issue `#78`.
4. Add OpenLineage and Marquez setup and interpretation documentation based on issues `#79` and `#80`.
5. Add validation evidence and readiness decision links from issue `#81`.
6. Update `documents/README.md`, `monitoring/README.md`, and `monitoring/STANDARDS.md`.
7. Update Airflow references if the final Phase 7 doc becomes the primary observability entry point.
8. Add known limitations and next-phase follow-up notes.
9. Refresh graphify memory after final docs are complete.

## Commit Plan (Issue #82)

1. `docs(observability): draft phase 7 handoff structure for issue 82`
2. `docs(observability): document metrics and prometheus setup for issue 82`
3. `docs(grafana): document dashboards and usage for issue 82`
4. `docs(logging): document pipeline log troubleshooting for issue 82`
5. `docs(openlineage): document lineage setup and interpretation for issue 82`
6. `docs(marquez): document lineage visualization usage for issue 82`
7. `docs(validation): link phase 7 coverage evidence for issue 82`
8. `docs(monitoring): update monitoring readme and standards for issue 82`
9. `docs(project): update documents index for phase 7 issue 82`
10. `docs(observability): publish final phase 7 limitations and handoff for issue 82`

## Acceptance Criteria Mapping

- metrics and dashboards documented: covered by metrics and dashboard documentation
- lineage setup and interpretation documented: covered by OpenLineage and Marquez sections
- troubleshooting guidelines added: covered by troubleshooting and operations runbook sections
- README and docs updated: covered by project index and monitoring index updates
- observability and lineage documentation is complete
- setup is reproducible for local development
- operators can troubleshoot metrics, logs, dashboards, and lineage delivery
- final handoff clearly explains what is implemented and what remains future scope

## Risk Notes

- docs can drift from implemented assets if written too early
- service-specific setup must distinguish required config from environment-specific values
- final handoff should avoid overstating live integrations that are only contract-validated
- too much detail can make the runbook hard to use; keep the final doc navigable
- screenshots can become stale quickly, so prefer text evidence unless screenshots are required
- final docs should distinguish local Data-Lab behavior from future Snowflake production direction

## Open Decision Log

- confirm final document name: `documents/observability-lineage.md`
- confirm whether dashboard screenshots are stored in `documents/assets/`
- confirm whether Phase 7 final doc should include commit ledger like Phase 6
- confirm whether `airflow/README.md` should point to Phase 7 docs as primary observability reference
- confirm whether troubleshooting lives entirely in `documents/observability-lineage.md` or is split into a separate runbook
