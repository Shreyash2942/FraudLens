# Phase 4 KPI Scenario Validation

Issue: `#55`

## Validation Asset

- dbt test file: `dbt/tests/validation/test_kpi_controlled_scenarios.sql`

## Covered Scenarios

1. Daily KPI count reconciliation
- compare `kpi_daily_fraud_operations.total_transactions` to fact-derived transaction counts by day
- compare `kpi_daily_fraud_operations.total_fraud_alerts` to fact-derived alert counts by day

2. Daily KPI ratio consistency
- compare `kpi_daily_fraud_operations.alert_rate_pct` to expected ratio:
  - `(fact_alert_count / fact_transaction_count) * 100`

3. Portfolio snapshot consistency
- compare latest `kpi_portfolio_risk_snapshot` total payment events and total fraud alerts against fact-derived totals

## Execution Command

```bash
dbt test --select test_kpi_controlled_scenarios --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

## Current Status

- execution date: `2026-05-17`
- status: `blocked`
- blocker: Hive thrift endpoint is not reachable (`127.0.0.1:10000`)
