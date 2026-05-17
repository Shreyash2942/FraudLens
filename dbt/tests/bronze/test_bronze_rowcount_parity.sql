with parity as (
    select
        'payment_instruction' as dataset_name,
        (select count(*) from {{ source('bronze', 'payment_instruction') }}) as source_count,
        (select count(*) from {{ ref('stg_bronze__payment_instruction') }}) as model_count
    union all
    select
        'payment_transaction' as dataset_name,
        (select count(*) from {{ source('bronze', 'payment_transaction') }}) as source_count,
        (select count(*) from {{ ref('stg_bronze__payment_transaction') }}) as model_count
    union all
    select
        'risk_signal' as dataset_name,
        (select count(*) from {{ source('bronze', 'risk_signal') }}) as source_count,
        (select count(*) from {{ ref('stg_bronze__risk_signal') }}) as model_count
    union all
    select
        'fraud_alert' as dataset_name,
        (select count(*) from {{ source('bronze', 'fraud_alert') }}) as source_count,
        (select count(*) from {{ ref('stg_bronze__fraud_alert') }}) as model_count
    union all
    select
        'fraud_case' as dataset_name,
        (select count(*) from {{ source('bronze', 'fraud_case') }}) as source_count,
        (select count(*) from {{ ref('stg_bronze__fraud_case') }}) as model_count
)
select
    dataset_name,
    source_count,
    model_count
from parity
where source_count != model_count
