# FraudLens dbt Project

This directory contains the Phase 4 dbt transformation foundation for FraudLens.

## Project Scope (Issue #48)

- dbt project scaffold and layer layout
- local Spark/Hive-compatible profile for container validation
- Snowflake profile templates (`dev`, `ci`, `prod`) for later cutover
- Bronze source metadata for all governed datasets
- shared macros for naming, audit, and batch filtering
- CI-ready structure validation commands

## Layout

- `dbt_project.yml` - core dbt project configuration
- `profiles/profiles.yml.example` - profile templates (Snowflake + local)
- `models/sources/` - source contracts
- `models/bronze/` - Bronze layer models (Phase 4 issue #49)
- `models/silver/` - Silver layer models (Phase 4 issue #50)
- `models/gold/` - Gold layer models (Phase 4 issues #51-#53)
- `macros/` - shared SQL/Jinja macros
- `scripts/` - validation helpers for local and CI execution

## Profiles and Targets

This repo keeps profile templates under `dbt/profiles/` so local and CI runs are deterministic.

- Snowflake profile: `fraudlens_snowflake`
  - targets: `dev`, `ci`, `prod`
- Local profile for container validation: `fraudlens_local_spark`
  - target: `local`

The local profile is the current default for structure checks (`parse`, `ls`) while Phase 4 is validated in the local stack.

## Required Environment Variables (Local Spark/Hive)

- `DBT_SPARK_HOST` (default: `localhost`)
- `DBT_SPARK_PORT` (default: `10000`)
- `DBT_SPARK_USER` (default: `datalab`)
- `DBT_SPARK_SCHEMA` (default: `default`)
- `DBT_SPARK_THREADS` (default: `4`)
- `DBT_SPARK_AUTH` (default: `NOSASL`)

## Snowflake Variables (Later Cutover)

- `DBT_SNOWFLAKE_ACCOUNT`
- `DBT_SNOWFLAKE_USER`
- `DBT_SNOWFLAKE_PASSWORD`
- `DBT_SNOWFLAKE_ROLE`
- `DBT_SNOWFLAKE_WAREHOUSE`
- `DBT_SNOWFLAKE_DATABASE`
- `DBT_SNOWFLAKE_DEV_SCHEMA`
- `DBT_SNOWFLAKE_CI_SCHEMA`
- `DBT_SNOWFLAKE_PROD_SCHEMA`
- `DBT_SNOWFLAKE_THREADS`

Optional local model vars:

- `DBT_FRAUDLENS_DATABASE` (default: `FRAUDLENS`)
- `DBT_FRAUDLENS_BRONZE_SCHEMA` (default: `BRONZE`)
- `DBT_FRAUDLENS_SILVER_SCHEMA` (default: `SILVER`)
- `DBT_FRAUDLENS_GOLD_SCHEMA` (default: `GOLD`)
- `DBT_FRAUDLENS_BATCH_ID` (default: empty string)

## Local Validation in Container (`fraudlens`)

From host machine:

```powershell
docker exec fraudlens sh -lc "cd /home/datalab/fraudlens && dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local"
docker exec fraudlens sh -lc "cd /home/datalab/fraudlens && dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local"
```

## CI/Automation Validation Commands

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

Or run helper script:

```bash
bash dbt/scripts/validate_structure.sh
```

Docs-generation validation:

```bash
bash dbt/scripts/validate_docs.sh
```

## Phase 5 Quality And Governance Controls

### Strict Validation Bundle

```bash
bash dbt/scripts/validate_structure.sh
```

Includes:
- selector gate coverage checks
- naming/governance/contract/failure-policy script checks
- fail-fast behavior for critical controls

### Diagnostic Validation Bundle

```bash
FRAUDLENS_VALIDATION_MODE=diagnostic bash dbt/scripts/validate_structure.sh
```

### Governance Readiness Artifact Capture

```bash
python dbt/scripts/capture_phase5_governance_readiness.py
```

Output:
- `documents/validation/data-quality-governance-readiness-artifacts.json`

### Related Governance Docs

- `documents/data-quality-governance.md`
