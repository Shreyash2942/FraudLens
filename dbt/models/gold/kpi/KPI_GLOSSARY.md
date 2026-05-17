# KPI Glossary

Canonical KPI definitions for Issue `#53`.

## Daily Fraud Operations KPIs

- `alert_rate_pct`
  - formula: `total_fraud_alerts / total_transactions * 100`
  - grain: day
- `high_severity_alert_rate_pct`
  - formula: `high_severity_alert_count / total_fraud_alerts * 100`
  - grain: day
- `fraud_case_open_rate_pct`
  - formula: `alerts_with_cases_count / total_fraud_alerts * 100`
  - grain: day
- `recovery_rate_pct`
  - formula: `total_recovered_amount / total_loss_amount * 100`
  - grain: day
- `reversal_rate_pct`
  - formula: `reversed_transaction_count / total_transactions * 100`
  - grain: day

## Portfolio Risk Snapshot KPIs

- `high_risk_payment_event_rate_pct`
  - formula: `high_risk_payment_event_count / total_payment_events * 100`
  - grain: snapshot
- `open_alert_backlog_rate_pct`
  - formula: `open_alert_count / total_fraud_alerts * 100`
  - grain: snapshot
- `open_case_backlog_rate_pct`
  - formula: `open_case_count / fraud_case_count * 100`
  - grain: snapshot
- `cross_border_transaction_rate_pct`
  - formula: `cross_border_transaction_count / total_transactions * 100`
  - grain: snapshot

## Calculation Contract

- zero or null denominator yields `0` (not null) in percentage KPIs
- percentages are expressed as numeric values in `[0, 100]` where applicable
- monetary aggregates preserve source currency assumptions from facts
