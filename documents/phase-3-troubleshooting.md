# Phase 3 Troubleshooting

This guide captures common issues for Phase 3 setup and Bronze load execution.

## 1) Connectivity Check Fails

Symptom:

- `check_connectivity.py` reports `FAIL` for MinIO or Trino host/port.

Actions:

1. Confirm local services are running in Data-Lab.
2. Verify `.env` values for `TRINO_HOST`, `TRINO_PORT`, and `MINIO_ENDPOINT`.
3. Re-run:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
```

## 2) Batch Manifest Missing

Symptom:

- `load_batch.py` raises `Manifest not found for batch`.

Actions:

1. Confirm synthetic generation completed:
   - `data/batches/<batch_id>/control/manifest.json` exists.
2. If unknown batch id, use the latest directory name under `data/batches/`.
3. Regenerate data if needed:

```powershell
py -m synthetic_generator.generate --mode mixed --output-dir data --profile small_fast --seed 42
```

## 3) Dataset Contract Mismatch

Symptom:

- dataset job contract emits `Layer mismatch` or `Dataset mismatch`.

Actions:

1. Ensure `--layer` and `--dataset` match the target job file.
2. Re-generate Bronze job templates:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/generate_layer_assets.py --layers bronze --clean --emit-spark-jobs
```

## 4) Snowflake Stage Or COPY Errors

Symptom:

- stage object not found, file format missing, or `COPY INTO` fails.

Actions:

1. Re-apply setup SQL in order:
   - `sql/ddl/create_database_and_schemas.sql`
   - `sql/ddl/create_roles_and_grants.sql`
   - `sql/staging/create_csv_file_format.sql`
   - `sql/staging/create_minio_external_stage.sql`
2. Verify object names align with active profile in `config/local.yml` or `config/cloud.yml`.
3. Rebuild batch SQL with:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_batch.py --batch-id <batch_id>
```

## 5) Local Spark Command Fails

Symptom:

- `run_dataset_spark_job.py` exits non-zero before job contract output.

Actions:

1. Test with script-only execution:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_dataset_spark_job.py --layer bronze --dataset region --batch-id <batch_id> --profile local --spark-submit-cmd python
```

2. If this succeeds, issue is with Spark runtime command. Validate local `spark-submit` installation and environment.
3. Optionally set `SPARK_SUBMIT_CMD` in `.env`.

## 6) Benchmark Script Returns Failures

Symptom:

- `benchmark_load.py` ends with failed runs.

Actions:

1. Inspect generated runtime benchmark markdown and JSON under:
   - `warehouse/snowflake-warehouse-setup/sql/runtime/performance/`
2. Identify failed dataset rows and run them individually with `run_dataset_spark_job.py`.
3. Re-run benchmark on a subset:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/benchmark_load.py --batch-id latest --datasets region,payment_instruction --runs 1 --spark-submit-cmd python
```

## 7) Validation Count Mismatch

Symptom:

- row-count validation does not match `manifest.json`.

Actions:

1. Verify dataset CSV exists at `data/batches/<batch_id>/landing/csv/<dataset>.csv`.
2. Confirm the same `batch_id` is used throughout generation, load SQL, and validation.
3. Re-run load SQL for only affected datasets before re-running validation queries.

## Escalation Checklist

Capture these artifacts before escalating:

- failing command and timestamp
- active profile (`local` or `cloud`)
- batch id
- relevant contract JSON output line
- generated SQL file from `warehouse/snowflake-warehouse-setup/sql/runtime/`
