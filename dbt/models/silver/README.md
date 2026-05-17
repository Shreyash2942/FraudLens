# Silver Models

Issue `#50` establishes the Silver dbt layer as the trusted conformed dataset surface.

## Design Intent

- clean and standardize source fields from Bronze staging models
- normalize data types and string formats for business-safe usage
- deduplicate records by business key (latest ingestion wins)
- preserve auditability fields needed for traceability
- apply lifecycle-safe transformations where event ordering can be invalid

## Model Pattern

Each model follows a consistent 3-step pattern:

1. `standardized`: type and format normalization from Bronze
2. `ranked`: business-key deduplication using `row_number()`
3. `business_safe`: rule guards for invalid lifecycle windows (where applicable)

## Naming and Build Output

- dbt model files: `slv__<dataset>.sql`
- built relation alias: `SILVER_<DATASET>`

## Validation Assets

- model tests: `dbt/models/silver/silver_models.yml`
- singular rules test: `dbt/tests/silver/test_silver_business_safe_rules.sql`

Recommended validation commands:

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local --select tag:silver
dbt test --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local --select tag:silver
```
