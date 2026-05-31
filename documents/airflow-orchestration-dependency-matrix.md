# Airflow Orchestration Dependency Matrix

Issue: `#73`
Last updated: `2026-05-30`

## Stage Dependencies

| From | To | Dependency Type | Failure Propagation |
|---|---|---|---|
| `prepare_runtime` | `ingestion_layer` | hard gate | downstream blocked |
| `ingestion_layer` | `transformation_layer` | hard gate | downstream blocked |
| `transformation_layer` | `validation_layer` | hard gate | downstream blocked |
| `validation_layer` | `publish_run_artifacts` | hard gate | summary not published on failure |

## Transformation Layer Dependencies

| Layer | Must Wait For | Gate Rule |
|---|---|---|
| `bronze` | runtime/context prepared | start of dbt chain |
| `silver` | `bronze` success | no partial progression |
| `gold` | `silver` success | no partial progression |
| `kpi` | `gold` success | terminal transform gate |

## Failure-State Mapping

| Condition | Expected State | Notes |
|---|---|---|
| upstream task fails | `upstream_failed` for dependents | default Airflow trigger rule behavior |
| deterministic contract failure | `failed` and stop progression | governed fail-fast behavior |
| infra transient failure | `up_for_retry` then `failed` if retries exhausted | retry policy by category |
| validation gate failure | `failed` | prevents publish/handoff |

## Retry/Timeout Linkage

Retry and timeout values are applied from profile policy map in:

- `airflow/config/orchestration_profiles.yml`
- `airflow/dags/_fraudlens_orchestration_common.py`

## Happy-Path Sequence

1. `prepare_runtime` resolves profile + batch + metadata context.
2. Ingestion completes and publishes ingestion summary.
3. Transformation executes `bronze -> silver -> gold -> kpi` with layer gate checks.
4. Validation runs critical selectors/policies and publishes validation summary.
5. Pipeline summary artifact is published.

## Failure + Recovery Sequence

1. A gate task fails (`failed`).
2. Downstream stage tasks enter `upstream_failed` unless trigger rules are explicitly overridden.
3. Failure metadata is emitted to failure artifact directory.
4. Operator remediates root cause and triggers rerun using the same or new batch context.
