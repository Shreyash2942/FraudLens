{{ config(tags=['quality', 'quality_critical', 'governance_critical', 'audit_critical', 'validation_critical']) }}

with violations as (
    select
        'slv__payment_instruction_to_stg_bronze__payment_instruction' as check_name,
        count(*) as violation_count
    from {{ ref('slv__payment_instruction') }} as slv
    left join {{ ref('stg_bronze__payment_instruction') }} as stg
        on slv.payment_instruction_id = stg.payment_instruction_id
       and slv.ingestion_batch_id = stg.ingestion_batch_id
    where stg.payment_instruction_id is null

    union all

    select
        'slv__payment_transaction_to_stg_bronze__payment_transaction' as check_name,
        count(*) as violation_count
    from {{ ref('slv__payment_transaction') }} as slv
    left join {{ ref('stg_bronze__payment_transaction') }} as stg
        on slv.payment_transaction_id = stg.payment_transaction_id
       and slv.ingestion_batch_id = stg.ingestion_batch_id
    where stg.payment_transaction_id is null

    union all

    select
        'fact_payment_events_to_slv__payment_instruction' as check_name,
        count(*) as violation_count
    from {{ ref('fact_payment_events') }} as fpe
    left join {{ ref('slv__payment_instruction') }} as slv
        on fpe.payment_instruction_id = slv.payment_instruction_id
       and fpe.ingestion_batch_id = slv.ingestion_batch_id
    where slv.payment_instruction_id is null

    union all

    select
        'fact_transactions_to_slv__payment_transaction' as check_name,
        count(*) as violation_count
    from {{ ref('fact_transactions') }} as ft
    left join {{ ref('slv__payment_transaction') }} as slv
        on ft.payment_transaction_id = slv.payment_transaction_id
       and ft.ingestion_batch_id = slv.ingestion_batch_id
    where slv.payment_transaction_id is null

    union all

    select
        'kpi_daily_fraud_operations_to_fact_daily_fraud_metrics' as check_name,
        count(*) as violation_count
    from {{ ref('kpi_daily_fraud_operations') }} as kpi
    left join {{ ref('fact_daily_fraud_metrics') }} as fdm
        on kpi.metric_date = fdm.metric_date
       and kpi.ingestion_batch_id = fdm.ingestion_batch_id
    where fdm.metric_date is null
)
select *
from violations
where violation_count > 0

