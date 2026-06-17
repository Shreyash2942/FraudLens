# Issue #66 Plan - Orchestration Strategy & DAG Design

Issue: `#66`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Define the orchestration pattern, DAG structure, and task boundaries for pipeline execution across ingestion, transformation, and validation.

## Task Breakdown

### 1) Define pipeline stages to orchestrate

Planned stage model:

1. `prepare_runtime`
2. `ingestion_layer`
3. `transformation_layer`
4. `validation_layer`
5. `publish_run_artifacts`

Stage intent:

- `prepare_runtime`: resolve profile, target, batch id, run id, and shared runtime context
- `ingestion_layer`: execute Bronze ingestion and stage/file checks
- `transformation_layer`: orchestrate dbt selectors by layer (`bronze`, `silver`, `gold`, `kpi`)
- `validation_layer`: run quality/governance/failure-policy gates
- `publish_run_artifacts`: store run metadata and summarized status for operations

### 2) Define DAG structure and task grouping

Planned DAG topology:

- master DAG: `fraudlens_phase6_pipeline_orchestration`
- supporting DAGs:
  - `fraudlens_phase6_ingestion_workflow`
  - `fraudlens_phase6_transformation_workflow`
  - `fraudlens_phase6_validation_workflow`

Task group shape in master DAG:

- `prepare_runtime`
- `ingestion_layer`
- `ingestion_complete_gate`
- `transformation_layer`
- `transformation_complete_gate`
- `validation_layer`
- `publish_run_artifacts`

### 3) Define dependency flow across ingestion, transformation, and validation

Dependency contract:

- strict stage progression: ingestion -> transformation -> validation
- no transformation starts until ingestion gate passes
- no validation starts until transformation gate passes
- critical validation failures block publish as `FAILED`
- non-critical warnings still publish run artifacts as `SUCCESS_WITH_WARNINGS`

Failure semantics:

- fail-fast for critical path tasks
- bounded retries for transient infra errors
- no retry for deterministic contract failures

### 4) Align DAG design with platform architecture

Architecture alignment decisions:

- local runtime path uses existing Spark/Hive execution scripts
- Snowflake-targeted orchestration remains profile-driven for later cutover
- dbt selectors and Phase 5 governance gates are reused instead of duplicating logic
- run metadata aligns with audit fields (`pipeline_run_id`, `source_system`, timestamps)

## Deliverables for Issue #66

- `airflow/dags/_fraudlens_phase6_common.py` (shared config + command builders)
- `airflow/config/phase6_profiles.yml` (runtime profile contract)
- `airflow/dags/fraudlens_phase6_pipeline_orchestration.py` (topology skeleton)
- `documents/phase-6-plan/issue-66-orchestration-strategy-dag-design.md` (this plan)
- `documents/orchestration-airflow.md` (master phase plan reference)

## Commit Plan (Issue #66)

1. `docs(airflow): define phase 6 orchestration architecture and dag topology for issue 66`
2. `feat(airflow): add phase 6 shared runtime profile contract for issue 66`
3. `docs(airflow): publish dependency matrix and control gates for issue 66`
4. `chore(airflow): add dag naming and operator standards for issue 66`

## Acceptance Criteria Mapping

- pipeline stages defined: covered by stage model and topology sections
- DAG structure and task grouping defined: covered by master/supporting DAG + task group design
- dependency flow defined: covered by dependency contract and failure semantics
- platform architecture alignment defined: covered by local/snowflake/profile/governance alignment decisions

## Open Decision Log

- confirm final milestone issue number (`#65` expected) if not created yet
- confirm if `#73` exists for documentation workstream
- confirm schedule default for master DAG (`None` vs daily in local)
