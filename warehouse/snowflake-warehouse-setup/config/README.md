# Phase 3 Config

This folder stores non-secret runtime profiles for Phase 3 setup.

## Files

- `local.yml`: local-first profile for container-based testing
- `cloud.yml`: cloud-ready profile for Snowflake execution
- `env.example`: required environment variable contract (copy values locally, do not commit secrets)

## Usage

- select profile with `PHASE3_ENV` (`local` or `cloud`)
- run `../scripts/print_runtime_config.py` to verify resolved settings
- keep credentials in local env files or secret manager, not in YAML

## Phase 3 Stage 4 Inputs

These profile files also define Bronze ingestion object names used by Stage 4 scripts:

- `warehouse.file_format_name` (default `FF_BRONZE_CSV_V1`)
- `warehouse.external_stage_name` (default `STG_BRONZE_MINIO_RAW`)

Required local secret values for MinIO stage setup:

- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `MINIO_PREFIX`

## Layer And Orchestration Controls

Phase 3 dataset-level orchestration uses additional non-secret controls in both `local.yml` and `cloud.yml`:

- `orchestration.mode`
  - default: `airflow`
  - options: `airflow`, `manual`
- `dependency_policy`
  - default: `bronze_strict`
- `layers.<layer>.enabled`
  - enables task generation for `bronze`, `silver`, `gold`
- `layers.<layer>.datasets`
  - set to `from_contract` to use governed `DATASET_ORDER`
  - or set explicit dataset list for targeted runs

Local Hive validation environment variables (used by local Bronze DAG and scripts):

- `HIVE_CMD` (default: `beeline`)
- `HIVE_JDBC_URL` (default: `jdbc:hive2://localhost:10000/default`)
- `HIVE_USER`
- `HIVE_PASSWORD`
- `HIVE_DATABASE` (default: `fraudlens_local`)
- `BRONZE_LOCAL_SPARK_CMD` (default: `python`, can be `spark-submit`)
