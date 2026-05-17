# Phase 4 Bronze-Silver-Gold Reconciliation Evidence

Issue: `#55`

## Reconciliation Test Asset

- dbt test file: `dbt/tests/validation/test_layer_reconciliation_core_flows.sql`
- objective: compare row-count consistency across key lineage paths:
  - Bronze -> Silver: payment instructions, payment transactions, risk signals, fraud alerts
  - Silver -> Gold: fact_payment_events, fact_transactions, fact_fraud_alerts

## Execution Command

```bash
dbt test --select test_layer_reconciliation_core_flows --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

## Current Status

- execution date: `2026-05-17`
- status: `blocked`
- blocker: Hive thrift endpoint `127.0.0.1:10000` not reachable from `fraudlens` container
- related build log: `documents/validation/issue-55-build-attempt-2026-05-17.log`

## Expected Pass Criteria

- each reconciliation check returns zero rows (no count mismatch)
- any non-zero delta is investigated and tracked before signoff
