# Issue #68 Plan - Build Transformation Workflow Tasks

Issue: `#68`  
Phase: `Phase 6 - Orchestration (Airflow)`  
Status date: `2026-05-25`

## Description Alignment

Implement Airflow transformation tasks that execute dbt models across Bronze, Silver, and Gold (plus KPI where applicable) with controlled context, staged dependency gates, and validation evidence.

## Task Breakdown

### 1) Create dbt run task definitions

Planned task groups:

- `transform_prepare`
- `transform_bronze`
- `transform_silver`
- `transform_gold`
- `transform_kpi`
- `transform_postcheck`

Planned core tasks:

- resolve dbt profile/target and runtime env vars
- run `dbt parse` preflight check
- run layer-specific dbt model execution commands using selectors/tags
- collect dbt command status and generated artifacts
- emit transformation summary metadata for downstream validation

Airflow structure:

- DAG: `fraudlens_phase6_transformation_workflow`
- TaskGroups:
  - `prepare_dbt_context`
  - `run_bronze_models`
  - `run_silver_models`
  - `run_gold_models`
  - `run_kpi_models`
  - `publish_transformation_metadata`

### 2) Separate transformation stages logically where needed

Stage separation policy:

- Bronze models run first to align source standardization
- Silver runs only after Bronze success gate
- Gold runs only after Silver success gate
- KPI runs only after Gold success gate
- optional selector override permits targeted reruns without breaking gate logic

Dependency contract:

- strict default progression: `bronze -> silver -> gold -> kpi`
- partial-run mode allowed only with explicit `allow_partial=true`
- critical model/test failures in any stage block downstream stages

Planned stage commands (local profile baseline):

- `dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local`
- `dbt run --select tag:bronze ...`
- `dbt run --select tag:silver ...`
- `dbt run --select tag:gold ...`
- `dbt run --select tag:kpi ...`

### 3) Configure environment and execution context

Required run-time parameters:

- `profile` (`fraudlens_local_spark`, future `fraudlens_snowflake`)
- `target` (`local`, `ci`, future `dev/prod`)
- `batch_id` (pass-through context for lineage metadata)
- `selector_override` (optional)
- `full_refresh_layers` (optional list for layer rerun)
- `threads` (default from profile/runtime env)

Execution context controls:

- centralized env resolution in `_fraudlens_phase6_common.py`
- explicit export of schema variables for Bronze/Silver/Gold
- stable working directory and command wrappers for reproducibility
- profile-driven behavior so local Spark/Hive remains default cost-saving path

### 4) Validate transformation task execution

Validation coverage:

- DAG import and syntax parse checks
- command contract tests for generated dbt commands
- dependency-order test for task graph
- sample local execution with artifact capture
- failure-branch evidence for blocked downstream stage

Expected evidence artifacts:

- transformation run summary JSON
- per-stage command outcome metadata
- selector counts and stage duration metrics
- failing command snippet for retry/failure policy checks

## Deliverables for Issue #68

- `airflow/dags/fraudlens_phase6_transformation_workflow.py`
- `airflow/dags/_fraudlens_phase6_common.py` (extended for dbt wrappers)
- `airflow/config/phase6_profiles.yml` (transformation runtime section)
- `airflow/tests/test_phase6_transformation_dag.py`
- `documents/phase-6-plan/issue-68-transformation-workflow-tasks.md` (this plan)

## Commit Plan (Issue #68)

1. `feat(airflow-transform): scaffold phase 6 transformation dag for issue 68`
2. `feat(airflow-transform): add dbt layer build task groups for issue 68`
3. `feat(airflow-transform): add layer dependency gates and selector controls for issue 68`
4. `feat(airflow-transform): capture dbt artifacts and status outputs for issue 68`
5. `test(airflow-transform): add transformation dag import and command contract tests for issue 68`

## Acceptance Criteria Mapping

- dbt run task definitions created: covered by task groups and command wrapper plan
- transformation stages separated logically: covered by stage policy and dependency gates
- environment/context configured: covered by parameter and runtime context contract
- transformation execution validated: covered by validation matrix and expected artifacts

## Risk Notes

- local adapter/runtime differences can affect dbt behavior versus Snowflake; keep profile-specific wrappers isolated
- layer retries may hide deterministic model defects; restrict retries for logic failures
- selector drift can skip critical models; include selector-count assertions in postcheck

## Open Decision Log

- confirm if KPI execution belongs inside `#68` or remains optional until `#69`
- confirm default `full_refresh` policy for Gold/KPI in local mode
- confirm max parallelism for dbt tasks in local container to avoid resource contention
