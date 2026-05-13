{{ config(alias='BRONZE_STG_DEPOSIT_ACCOUNT', tags=['bronze', 'staging_raw']) }}

select
    src.DEPOSIT_ACCOUNT_ID as deposit_account_id,
    src.ACCOUNT_STATUS as account_status,
    src.PRODUCT_TYPE_CODE as product_type_code,
    src.PRIMARY_PARTY_ID as primary_party_id,
    src.ACCOUNT_CURRENCY_CODE as account_currency_code,
    src.AVAILABLE_BALANCE_AMOUNT as available_balance_amount,
    src.OPENED_AT as opened_at,
    src.OPENED_BRANCH_ID as opened_branch_id,
    src.SERVICING_BUSINESS_UNIT_ID as servicing_business_unit_id,
    src.ACCOUNT_REGION_ID as account_region_id,
    src.CLOSED_AT as closed_at,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'deposit_account') }} as src
{{ fraudlens_batch_where('src') }}
