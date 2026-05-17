with reconciliation as (
    select
        'bronze_to_silver.payment_instruction' as check_name,
        (select count(*) from {{ ref('stg_bronze__payment_instruction') }}) as upstream_count,
        (select count(*) from {{ ref('slv__payment_instruction') }}) as downstream_count
    union all
    select
        'bronze_to_silver.payment_transaction' as check_name,
        (select count(*) from {{ ref('stg_bronze__payment_transaction') }}) as upstream_count,
        (select count(*) from {{ ref('slv__payment_transaction') }}) as downstream_count
    union all
    select
        'bronze_to_silver.risk_signal' as check_name,
        (select count(*) from {{ ref('stg_bronze__risk_signal') }}) as upstream_count,
        (select count(*) from {{ ref('slv__risk_signal') }}) as downstream_count
    union all
    select
        'bronze_to_silver.fraud_alert' as check_name,
        (select count(*) from {{ ref('stg_bronze__fraud_alert') }}) as upstream_count,
        (select count(*) from {{ ref('slv__fraud_alert') }}) as downstream_count
    union all
    select
        'silver_to_gold.fact_payment_events' as check_name,
        (select count(*) from {{ ref('slv__payment_instruction') }}) as upstream_count,
        (select count(*) from {{ ref('fact_payment_events') }}) as downstream_count
    union all
    select
        'silver_to_gold.fact_transactions' as check_name,
        (select count(*) from {{ ref('slv__payment_transaction') }}) as upstream_count,
        (select count(*) from {{ ref('fact_transactions') }}) as downstream_count
    union all
    select
        'silver_to_gold.fact_fraud_alerts' as check_name,
        (select count(*) from {{ ref('slv__fraud_alert') }}) as upstream_count,
        (select count(*) from {{ ref('fact_fraud_alerts') }}) as downstream_count
),
violations as (
    select
        check_name,
        upstream_count,
        downstream_count,
        downstream_count - upstream_count as delta_count
    from reconciliation
    where downstream_count <> upstream_count
)
select *
from violations
