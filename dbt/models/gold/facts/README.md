# Gold Fact Models

Issue `#51` implements analytics-ready fact models at explicit business grain for fraud analytics reporting.

## Implemented Models

- `fact_transactions` (`GOLD_FACT_TRANSACTIONS`)
  - grain: one row per `payment_transaction_id`
  - purpose: transaction execution analytics with payment context and fraud exposure counters
- `fact_fraud_alerts` (`GOLD_FACT_FRAUD_ALERTS`)
  - grain: one row per `fraud_alert_id`
  - purpose: alert operations, SLA, and case/decision/disposition outcome analytics
- `fact_payment_events` (`GOLD_FACT_PAYMENT_EVENTS`)
  - grain: one row per `payment_instruction_id`
  - purpose: end-to-end payment event timeline and conversion-to-fraud funnel metrics
- `fact_daily_fraud_metrics` (`GOLD_FACT_DAILY_FRAUD_METRICS`)
  - grain: one row per `metric_date`
  - purpose: daily KPI-ready aggregates for transactions, alerts, risk, and case activity

## Design Notes

- Gold facts source from conformed Silver models only.
- Facts preserve audit trace fields (`ingestion_batch_id`, `source_file_name`, `ingested_at_utc`, `pipeline_processed_at_utc`, `lineage_run_id`) wherever source grain permits.
- Daily metrics use `slv__calendar_day` as the date spine over observed event-date bounds.

## Validation Assets

- model tests: `dbt/models/gold/facts/gold_fact_models.yml`
- singular test: `dbt/tests/gold/test_fact_daily_fraud_metrics_nonnegative.sql`

Recommended checks:

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local --select tag:gold
dbt test --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local --select tag:gold
```
