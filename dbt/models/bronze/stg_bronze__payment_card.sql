{{ config(alias='bronze_stg_payment_card', tags=['bronze', 'staging_raw']) }}

select
    src.CARD_ID as card_id,
    src.LINKED_ACCOUNT_ID as linked_account_id,
    src.CARD_STATUS as card_status,
    src.CARD_NETWORK_CODE as card_network_code,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'payment_card') }} as src
{{ fraudlens_batch_where('src') }}
