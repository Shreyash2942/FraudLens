{{ config(tags=['quality', 'quality_critical', 'gold', 'kpi', 'tier_1_critical']) }}

with expected_daily as (
    select
        ft.transaction_date as metric_date,
        count(ft.payment_transaction_id) as expected_total_transactions,
        count(fa.fraud_alert_id) as expected_total_fraud_alerts,
        case
            when count(ft.payment_transaction_id) = 0 then cast(0.0 as double)
            else cast(100.0 * count(fa.fraud_alert_id) / count(ft.payment_transaction_id) as double)
        end as expected_alert_rate_pct
    from {{ ref('fact_transactions') }} as ft
    left join {{ ref('fact_fraud_alerts') }} as fa
        on ft.payment_instruction_id = fa.payment_instruction_id
       and fa.alert_created_date = ft.transaction_date
    where ft.transaction_date is not null
    group by ft.transaction_date
),
daily_comparison as (
    select
        'kpi_daily_fraud_operations' as model_name,
        cast(kpi.metric_date as string) as grain_id,
        kpi.total_transactions as actual_total_transactions,
        exp.expected_total_transactions as expected_total_transactions,
        kpi.total_fraud_alerts as actual_total_fraud_alerts,
        exp.expected_total_fraud_alerts as expected_total_fraud_alerts,
        kpi.alert_rate_pct as actual_alert_rate_pct,
        exp.expected_alert_rate_pct as expected_alert_rate_pct
    from {{ ref('kpi_daily_fraud_operations') }} as kpi
    inner join expected_daily as exp
        on kpi.metric_date = exp.metric_date
    where kpi.total_transactions <> exp.expected_total_transactions
       or kpi.total_fraud_alerts <> exp.expected_total_fraud_alerts
       or abs(kpi.alert_rate_pct - exp.expected_alert_rate_pct) > 0.0001
),
snapshot_expected as (
    select
        count(distinct fpe.payment_instruction_id) as expected_total_payment_events,
        count(distinct fa.fraud_alert_id) as expected_total_fraud_alerts
    from {{ ref('fact_payment_events') }} as fpe
    left join {{ ref('fact_fraud_alerts') }} as fa
        on fpe.payment_instruction_id = fa.payment_instruction_id
),
snapshot_latest as (
    select *
    from {{ ref('kpi_portfolio_risk_snapshot') }}
    order by snapshot_at_utc desc
    limit 1
),
snapshot_comparison as (
    select
        'kpi_portfolio_risk_snapshot' as model_name,
        cast(snp.snapshot_at_utc as string) as grain_id,
        snp.total_payment_events as actual_total_transactions,
        exp.expected_total_payment_events as expected_total_transactions,
        snp.total_fraud_alerts as actual_total_fraud_alerts,
        exp.expected_total_fraud_alerts as expected_total_fraud_alerts,
        cast(null as double) as actual_alert_rate_pct,
        cast(null as double) as expected_alert_rate_pct
    from snapshot_latest as snp
    cross join snapshot_expected as exp
    where snp.total_payment_events <> exp.expected_total_payment_events
       or snp.total_fraud_alerts <> exp.expected_total_fraud_alerts
)
select *
from daily_comparison
union all
select *
from snapshot_comparison
