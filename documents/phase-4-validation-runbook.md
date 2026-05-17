# Phase 4 Validation Runbook

Runbook for validating Bronze, Silver, Gold, KPI, and governance assets for Issues `#48` through `#55`.

## Prerequisites

- local runtime container: `fraudlens`
- Hive/Spark services running in container
- dbt profiles configured for local target

## Environment Variables

```powershell
$env:DBT_FRAUDLENS_BRONZE_SCHEMA='bronze'
$env:DBT_FRAUDLENS_SILVER_SCHEMA='silver'
$env:DBT_FRAUDLENS_GOLD_SCHEMA='gold'
$env:DBT_HIVE_USAGE_TRACKING='false'
```

## Core Validation Commands

```bash
cd /home/datalab/fraudlens/dbt
dbt parse --profiles-dir profiles --profile fraudlens_local_spark --target local
dbt build --select tag:bronze --profiles-dir profiles --profile fraudlens_local_spark --target local
dbt build --select tag:silver --profiles-dir profiles --profile fraudlens_local_spark --target local
dbt build --select tag:gold --full-refresh --profiles-dir profiles --profile fraudlens_local_spark --target local
dbt build --select tag:kpi --full-refresh --profiles-dir profiles --profile fraudlens_local_spark --target local
```

## Targeted Governance/Validation Tests

```bash
dbt test --select test_fact_dimension_relationships --profiles-dir profiles --profile fraudlens_local_spark --target local
dbt test --select test_governance_required_audit_columns --profiles-dir profiles --profile fraudlens_local_spark --target local
dbt test --select test_kpi_rate_guardrails --profiles-dir profiles --profile fraudlens_local_spark --target local
```

## Expected Signals

- `dbt parse` succeeds with no compilation errors
- all model layers build successfully
- test suites report `ERROR=0`
- key Gold tables populate with non-zero row counts
- KPI tables expose non-null rates and bounded percentage values

## Failure Handling

- if local Hive strict mode blocks SQL patterns, refactor SQL to remove unsupported cross joins/subqueries
- for incremental model duplicate failures, run `--full-refresh` for clean validation
- capture failing compiled SQL from `target/compiled/...` for issue notes
