with source_counts as (
    select 'payment_instruction' as dataset_name, count(*) as source_count
    from {{ source('bronze', 'payment_instruction') }}
    union all
    select 'payment_transaction' as dataset_name, count(*) as source_count
    from {{ source('bronze', 'payment_transaction') }}
    union all
    select 'risk_signal' as dataset_name, count(*) as source_count
    from {{ source('bronze', 'risk_signal') }}
    union all
    select 'fraud_alert' as dataset_name, count(*) as source_count
    from {{ source('bronze', 'fraud_alert') }}
    union all
    select 'fraud_case' as dataset_name, count(*) as source_count
    from {{ source('bronze', 'fraud_case') }}
),
model_counts as (
    select 'payment_instruction' as dataset_name, count(*) as model_count
    from {{ ref('stg_bronze__payment_instruction') }}
    union all
    select 'payment_transaction' as dataset_name, count(*) as model_count
    from {{ ref('stg_bronze__payment_transaction') }}
    union all
    select 'risk_signal' as dataset_name, count(*) as model_count
    from {{ ref('stg_bronze__risk_signal') }}
    union all
    select 'fraud_alert' as dataset_name, count(*) as model_count
    from {{ ref('stg_bronze__fraud_alert') }}
    union all
    select 'fraud_case' as dataset_name, count(*) as model_count
    from {{ ref('stg_bronze__fraud_case') }}
),
parity as (
    select
        source_counts.dataset_name,
        source_counts.source_count,
        model_counts.model_count
    from source_counts
    inner join model_counts
        on source_counts.dataset_name = model_counts.dataset_name
)
select
    dataset_name,
    source_count,
    model_count
from parity
where source_count != model_count
