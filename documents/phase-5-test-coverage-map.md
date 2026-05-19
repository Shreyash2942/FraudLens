# Phase 5 dbt Test Coverage Map

## Purpose

This document maps core FraudLens models to quality test categories and selector usage introduced in Phase 5 issue `#58`.

## Test Categories

- `quality_not_null`
- `quality_unique`
- `quality_relationships`
- `quality_accepted_values`
- `quality_critical_gate`
- `quality_high_gate`

## Core Model Coverage

### Bronze Critical Models

- `stg_bronze__payment_instruction`
- `stg_bronze__payment_transaction`
- `stg_bronze__risk_signal`
- `stg_bronze__fraud_alert`
- `stg_bronze__fraud_case`

Coverage:
- `not_null` key + audit columns
- `unique` key checks
- source freshness policy in source contracts

### Silver Critical Models

- `slv__payment_instruction`
- `slv__payment_transaction`
- `slv__risk_signal`
- `slv__fraud_alert`
- `slv__fraud_case`
- `slv__decision_record`
- `slv__case_disposition`

Coverage:
- `not_null` + `unique` canonical identifiers
- `relationships` for governed lifecycle links
- `accepted_values` for controlled status/severity/type fields

### Gold Fact Models

- `fact_transactions`
- `fact_payment_events`
- `fact_fraud_alerts`
- `fact_daily_fraud_metrics`

Coverage:
- fact grain `not_null` + `unique`
- critical relationships to upstream Silver models
- integrity and aggregate sanity checks via singular tests

### Gold Dimension Models

- `dim_customer`, `dim_account`, `dim_card`, `dim_customer_org_assignment`
- `dim_branch`, `dim_business_unit`, `dim_analyst_team`, `dim_region`, `dim_date`
- `dim_device`, `dim_channel`, `dim_merchant`, `dim_reference_code`

Coverage:
- completeness checks on dimensional keys
- uniqueness checks for core dimensional identifiers
- relationship checks for hierarchy/conformance paths

### KPI Models

- `kpi_daily_fraud_operations`
- `kpi_portfolio_risk_snapshot`

Coverage:
- KPI key completeness/uniqueness
- bounded-rate guardrails (`0..100`)
- controlled scenario consistency checks against fact-derived expectations

## Selector Usage

### Critical Gate

```bash
dbt test --selector quality_critical_gate --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### High-Severity Gate

```bash
dbt test --selector quality_high_gate --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### Category Runs

```bash
dbt test --selector quality_not_null --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_unique --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_relationships --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_accepted_values --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### Layer Runs

```bash
dbt test --selector quality_bronze --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_silver --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_gold --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

## Notes

- `quality_critical_gate` is the default fail-fast execution path.
- `quality_high_gate` supports readiness-risk review before release/signoff.
- this coverage map is the baseline for Phase 5 issues `#62` and `#63`.
