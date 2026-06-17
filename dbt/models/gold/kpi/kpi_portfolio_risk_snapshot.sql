{{ config(alias='gold_kpi_portfolio_risk_snapshot', tags=['gold', 'kpi']) }}

with payment_event_rollup as (
    select
        count(*) as total_payment_events,
        sum(coalesce(pe.high_risk_signal_count, 0)) as total_high_risk_signals,
        sum(case when pe.is_high_risk_payment_event then 1 else 0 end) as high_risk_payment_event_count,
        sum(coalesce(pe.open_alert_count, 0)) as open_alert_count,
        sum(coalesce(pe.fraud_alert_count, 0)) as total_fraud_alerts,
        sum(coalesce(pe.open_case_count, 0)) as open_case_count,
        sum(coalesce(pe.fraud_case_count, 0)) as fraud_case_count,
        max(pe.ingestion_batch_id) as ingestion_batch_id,
        max(pe.source_file_name) as source_file_name,
        max(pe.ingested_at_utc) as ingested_at_utc,
        max(pe.created_at_utc) as created_at_utc,
        max(pe.updated_at_utc) as updated_at_utc,
        max(pe.source_system) as source_system,
        max(pe.pipeline_run_id) as pipeline_run_id,
        max(pe.pipeline_processed_at_utc) as pipeline_processed_at_utc,
        max(pe.lineage_run_id) as lineage_run_id
    from {{ ref('fact_payment_events') }} as pe
),
daily_rollup as (
    select
        sum(coalesce(dm.total_transactions, 0)) as total_transactions,
        sum(coalesce(dm.cross_border_transaction_count, 0)) as cross_border_transaction_count,
        sum(coalesce(dm.total_loss_amount, 0)) as total_loss_amount,
        sum(coalesce(dm.total_recovered_amount, 0)) as total_recovered_amount
    from {{ ref('fact_daily_fraud_metrics') }} as dm
)
select
    current_timestamp as snapshot_at_utc,
    pe.total_payment_events,
    pe.total_high_risk_signals,
    pe.high_risk_payment_event_count,
    pe.total_fraud_alerts,
    pe.open_alert_count,
    pe.fraud_case_count,
    pe.open_case_count,
    dr.total_transactions,
    dr.cross_border_transaction_count,
    dr.total_loss_amount,
    dr.total_recovered_amount,
    {{ fraudlens_pct('pe.high_risk_payment_event_count', 'pe.total_payment_events') }} as high_risk_payment_event_rate_pct,
    {{ fraudlens_pct('pe.open_alert_count', 'pe.total_fraud_alerts') }} as open_alert_backlog_rate_pct,
    {{ fraudlens_pct('pe.open_case_count', 'pe.fraud_case_count') }} as open_case_backlog_rate_pct,
    {{ fraudlens_pct('dr.cross_border_transaction_count', 'dr.total_transactions') }} as cross_border_transaction_rate_pct,
    {{ fraudlens_pct('dr.total_recovered_amount', 'dr.total_loss_amount') }} as portfolio_recovery_rate_pct,
    pe.ingestion_batch_id,
    pe.source_file_name,
    pe.ingested_at_utc,
    pe.created_at_utc,
    pe.updated_at_utc,
    pe.source_system,
    pe.pipeline_run_id,
    pe.pipeline_processed_at_utc,
    pe.lineage_run_id
from payment_event_rollup as pe
cross join daily_rollup as dr
