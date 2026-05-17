# Gold KPI Models

Issue `#53` centralizes canonical fraud analytics metrics for consistent BI and downstream consumption.

## KPI Contract Principles

- KPI numerators and denominators are defined once in Gold KPI models.
- Rate metrics use shared safe-division macros to avoid null/zero-denominator inconsistencies.
- KPI grain is explicit in each model:
  - daily operational metrics at `metric_date`
  - portfolio snapshots at run-time snapshot timestamp
- KPI logic is sourced from Gold fact models only.

## Primary KPI Models

- `kpi_daily_fraud_operations` (`GOLD_KPI_DAILY_FRAUD_OPERATIONS`)
- `kpi_portfolio_risk_snapshot` (`GOLD_KPI_PORTFOLIO_RISK_SNAPSHOT`)

## Reference Glossary

See `KPI_GLOSSARY.md` for metric definitions and formula contracts.
