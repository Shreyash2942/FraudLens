# KPI Lineage

## `kpi_daily_fraud_operations`

- upstream facts:
  - `fact_daily_fraud_metrics`
- metric groups:
  - alert volume and severity
  - case conversion
  - recovery and reversal outcomes

## `kpi_portfolio_risk_snapshot`

- upstream facts:
  - `fact_payment_events`
  - `fact_daily_fraud_metrics`
- metric groups:
  - high-risk event concentration
  - alert/case backlog posture
  - cross-border and recovery posture

## Operational Notes

- expected grain:
  - daily model: one row per `metric_date`
  - snapshot model: one row per build invocation
- percentage metrics are standardized using shared KPI macros.
