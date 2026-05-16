{{ config(alias='GOLD_FACT_DAILY_FRAUD_METRICS', tags=['gold', 'fact']) }}

with transaction_daily as (
    select
        ft.transaction_date as metric_date,
        count(ft.payment_transaction_id) as total_transactions,
        sum(coalesce(ft.booking_amount, 0)) as total_transaction_amount,
        sum(case when ft.is_cross_border then 1 else 0 end) as cross_border_transaction_count,
        sum(case when ft.is_reversal then 1 else 0 end) as reversed_transaction_count,
        max(ft.ingestion_batch_id) as ingestion_batch_id,
        max(ft.source_file_name) as source_file_name,
        max(ft.ingested_at_utc) as ingested_at_utc,
        max(ft.pipeline_processed_at_utc) as pipeline_processed_at_utc,
        max(ft.lineage_run_id) as lineage_run_id
    from {{ ref('fact_transactions') }} as ft
    where ft.transaction_date is not null
    group by ft.transaction_date
),
alert_daily as (
    select
        fa.alert_created_date as metric_date,
        count(fa.fraud_alert_id) as total_fraud_alerts,
        sum(case when fa.is_high_severity_alert then 1 else 0 end) as high_severity_alert_count,
        sum(case when fa.is_sla_breached then 1 else 0 end) as sla_breached_alert_count,
        sum(case when fa.fraud_case_id is not null then 1 else 0 end) as alerts_with_cases_count,
        sum(coalesce(fa.total_loss_amount, 0)) as total_loss_amount,
        sum(coalesce(fa.total_recovered_amount, 0)) as total_recovered_amount,
        max(fa.ingestion_batch_id) as ingestion_batch_id,
        max(fa.source_file_name) as source_file_name,
        max(fa.ingested_at_utc) as ingested_at_utc,
        max(fa.pipeline_processed_at_utc) as pipeline_processed_at_utc,
        max(fa.lineage_run_id) as lineage_run_id
    from {{ ref('fact_fraud_alerts') }} as fa
    where fa.alert_created_date is not null
    group by fa.alert_created_date
),
payment_event_daily as (
    select
        fpe.payment_event_date as metric_date,
        count(fpe.payment_instruction_id) as total_payment_events,
        sum(coalesce(fpe.risk_signal_count, 0)) as total_risk_signals,
        sum(coalesce(fpe.fraud_alert_count, 0)) as total_alerts_from_events,
        sum(coalesce(fpe.fraud_case_count, 0)) as total_cases_from_events,
        sum(case when fpe.is_high_risk_payment_event then 1 else 0 end) as high_risk_payment_event_count,
        max(fpe.ingestion_batch_id) as ingestion_batch_id,
        max(fpe.source_file_name) as source_file_name,
        max(fpe.ingested_at_utc) as ingested_at_utc,
        max(fpe.pipeline_processed_at_utc) as pipeline_processed_at_utc,
        max(fpe.lineage_run_id) as lineage_run_id
    from {{ ref('fact_payment_events') }} as fpe
    where fpe.payment_event_date is not null
    group by fpe.payment_event_date
),
metric_dates as (
    select metric_date from transaction_daily
    union
    select metric_date from alert_daily
    union
    select metric_date from payment_event_daily
),
calendar_spine as (
    select
        cal.calendar_date as metric_date,
        cal.calendar_year,
        cal.calendar_quarter,
        cal.calendar_month,
        cal.calendar_month_name,
        cal.week_of_year,
        cal.day_of_week,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday
    from {{ ref('slv__calendar_day') }} as cal
    inner join metric_dates as md
        on cal.calendar_date = md.metric_date
)
select
    md5(cast(sp.metric_date as string)) as fact_daily_fraud_metrics_sk,
    sp.metric_date,
    sp.calendar_year,
    sp.calendar_quarter,
    sp.calendar_month,
    sp.calendar_month_name,
    sp.week_of_year,
    sp.day_of_week,
    sp.day_name,
    sp.is_weekend,
    sp.is_holiday,
    coalesce(td.total_transactions, 0) as total_transactions,
    coalesce(td.total_transaction_amount, 0) as total_transaction_amount,
    coalesce(td.cross_border_transaction_count, 0) as cross_border_transaction_count,
    coalesce(td.reversed_transaction_count, 0) as reversed_transaction_count,
    coalesce(ad.total_fraud_alerts, 0) as total_fraud_alerts,
    coalesce(ad.high_severity_alert_count, 0) as high_severity_alert_count,
    coalesce(ad.sla_breached_alert_count, 0) as sla_breached_alert_count,
    coalesce(ad.alerts_with_cases_count, 0) as alerts_with_cases_count,
    coalesce(ad.total_loss_amount, 0) as total_loss_amount,
    coalesce(ad.total_recovered_amount, 0) as total_recovered_amount,
    coalesce(ped.total_payment_events, 0) as total_payment_events,
    coalesce(ped.total_risk_signals, 0) as total_risk_signals,
    coalesce(ped.total_alerts_from_events, 0) as total_alerts_from_events,
    coalesce(ped.total_cases_from_events, 0) as total_cases_from_events,
    coalesce(ped.high_risk_payment_event_count, 0) as high_risk_payment_event_count,
    coalesce(td.ingestion_batch_id, ad.ingestion_batch_id, ped.ingestion_batch_id) as ingestion_batch_id,
    coalesce(td.source_file_name, ad.source_file_name, ped.source_file_name) as source_file_name,
    coalesce(td.ingested_at_utc, ad.ingested_at_utc, ped.ingested_at_utc) as ingested_at_utc,
    coalesce(td.pipeline_processed_at_utc, ad.pipeline_processed_at_utc, ped.pipeline_processed_at_utc) as pipeline_processed_at_utc,
    coalesce(td.lineage_run_id, ad.lineage_run_id, ped.lineage_run_id) as lineage_run_id
from calendar_spine as sp
left join transaction_daily as td
    on sp.metric_date = td.metric_date
left join alert_daily as ad
    on sp.metric_date = ad.metric_date
left join payment_event_daily as ped
    on sp.metric_date = ped.metric_date
