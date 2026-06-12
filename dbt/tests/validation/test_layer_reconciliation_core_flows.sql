with upstream_counts as (
    select
        'bronze_to_silver.payment_instruction' as check_name,
        count(*) as upstream_count
    from {{ ref('stg_bronze__payment_instruction') }}
    union all
    select
        'bronze_to_silver.payment_transaction' as check_name,
        count(*) as upstream_count
    from {{ ref('stg_bronze__payment_transaction') }}
    union all
    select
        'bronze_to_silver.risk_signal' as check_name,
        count(*) as upstream_count
    from {{ ref('stg_bronze__risk_signal') }}
    union all
    select
        'bronze_to_silver.fraud_alert' as check_name,
        count(*) as upstream_count
    from {{ ref('stg_bronze__fraud_alert') }}
    union all
    select
        'silver_to_gold.fact_payment_events' as check_name,
        count(*) as upstream_count
    from {{ ref('slv__payment_instruction') }}
    union all
    select
        'silver_to_gold.fact_transactions' as check_name,
        count(*) as upstream_count
    from {{ ref('slv__payment_transaction') }}
    union all
    select
        'silver_to_gold.fact_fraud_alerts' as check_name,
        count(*) as upstream_count
    from {{ ref('slv__fraud_alert') }}
),
downstream_counts as (
    select
        'bronze_to_silver.payment_instruction' as check_name,
        count(*) as downstream_count
    from {{ ref('slv__payment_instruction') }}
    union all
    select
        'bronze_to_silver.payment_transaction' as check_name,
        count(*) as downstream_count
    from {{ ref('slv__payment_transaction') }}
    union all
    select
        'bronze_to_silver.risk_signal' as check_name,
        count(*) as downstream_count
    from {{ ref('slv__risk_signal') }}
    union all
    select
        'bronze_to_silver.fraud_alert' as check_name,
        count(*) as downstream_count
    from {{ ref('slv__fraud_alert') }}
    union all
    select
        'silver_to_gold.fact_payment_events' as check_name,
        count(*) as downstream_count
    from {{ ref('fact_payment_events') }}
    union all
    select
        'silver_to_gold.fact_transactions' as check_name,
        count(*) as downstream_count
    from {{ ref('fact_transactions') }}
    union all
    select
        'silver_to_gold.fact_fraud_alerts' as check_name,
        count(*) as downstream_count
    from {{ ref('fact_fraud_alerts') }}
),
reconciliation as (
    select
        upstream_counts.check_name,
        upstream_counts.upstream_count,
        downstream_counts.downstream_count
    from upstream_counts
    inner join downstream_counts
        on upstream_counts.check_name = downstream_counts.check_name
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
