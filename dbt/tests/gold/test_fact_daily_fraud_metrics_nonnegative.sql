select
    metric_date
from {{ ref('fact_daily_fraud_metrics') }}
where total_transactions < 0
   or total_transaction_amount < 0
   or cross_border_transaction_count < 0
   or reversed_transaction_count < 0
   or total_fraud_alerts < 0
   or high_severity_alert_count < 0
   or sla_breached_alert_count < 0
   or alerts_with_cases_count < 0
   or total_loss_amount < 0
   or total_recovered_amount < 0
   or total_payment_events < 0
   or total_risk_signals < 0
   or total_alerts_from_events < 0
   or total_cases_from_events < 0
   or high_risk_payment_event_count < 0
