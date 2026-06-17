# Bronze Models

Issue `#49` establishes the Bronze dbt layer as the governed access point for raw ingested warehouse data.

## Design Intent

- preserve source fidelity (1:1 row-level representation from Bronze sources)
- apply minimal transformation only:
  - column naming standardized to lowercase snake_case
  - shared audit passthrough via `fraudlens_pipeline_audit_projection('src')`
- keep optional batch-level filtering via `fraudlens_batch_where('src')`

## Source Contract

- Bronze sources are declared in `dbt/models/sources/bronze_sources.yml`
- models read only from `source('bronze', '<dataset>')`

## Model Naming

- dbt model files: `stg_bronze__<dataset>.sql`
- built relation alias: `bronze_stg_<dataset>`

This avoids collisions with raw Bronze tables named `BRONZE_<DATASET>`.

## Validation Assets

- key model tests are defined in `dbt/models/bronze/bronze_models.yml`
- parity test: `dbt/tests/bronze/test_bronze_rowcount_parity.sql`

Recommended checks:

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local --select tag:bronze
dbt test --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local --select tag:bronze
```
