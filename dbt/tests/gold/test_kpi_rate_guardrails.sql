with daily_violations as (
    select
        metric_date as row_key,
        'kpi_daily_fraud_operations' as model_name,
        'rate_out_of_bounds' as issue
    from {{ ref('kpi_daily_fraud_operations') }}
    where alert_rate_pct < 0
       or high_severity_alert_rate_pct < 0
       or high_severity_alert_rate_pct > 100
       or fraud_case_open_rate_pct < 0
       or fraud_case_open_rate_pct > 100
       or recovery_rate_pct < 0
       or reversal_rate_pct < 0
       or reversal_rate_pct > 100
),
snapshot_violations as (
    select
        cast(snapshot_at_utc as string) as row_key,
        'kpi_portfolio_risk_snapshot' as model_name,
        'rate_out_of_bounds' as issue
    from {{ ref('kpi_portfolio_risk_snapshot') }}
    where high_risk_payment_event_rate_pct < 0
       or high_risk_payment_event_rate_pct > 100
       or open_alert_backlog_rate_pct < 0
       or open_alert_backlog_rate_pct > 100
       or open_case_backlog_rate_pct < 0
       or open_case_backlog_rate_pct > 100
       or cross_border_transaction_rate_pct < 0
       or cross_border_transaction_rate_pct > 100
       or portfolio_recovery_rate_pct < 0
)
select * from daily_violations
union all
select * from snapshot_violations
