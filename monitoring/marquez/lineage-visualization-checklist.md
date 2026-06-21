# Marquez Lineage Visualization Checklist

Use this checklist after delivering OpenLineage events to Marquez.

## Service Checks

- Marquez API responds at `MARQUEZ_BASE_URL`.
- OpenLineage receiver is configured through `OPENLINEAGE_URL`.
- Health evidence is captured with `scripts/check_marquez_health.py`.

## UI Checks

- FraudLens namespace appears in Marquez.
- Airflow pipeline job appears for `fraudlens_pipeline_orchestration`.
- dbt transformation jobs appear with `dbt.model...` names.
- Input batch datasets appear as upstream nodes.
- Transformation outputs appear as downstream nodes.
- Run facets include `pipeline_run_id`, `batch_id`, and `run_profile`.

## Evidence to Capture

- Marquez URL
- namespace name
- job name
- run ID
- visible upstream dataset
- visible downstream dataset
- screenshot or exported API response when available
