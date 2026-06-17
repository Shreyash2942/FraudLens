{{ config(alias='bronze_stg_case_disposition', tags=['bronze', 'staging_raw']) }}

select
    src.DISPOSITION_ID as disposition_id,
    src.DECISION_ID as decision_id,
    src.DISPOSITION_CODE as disposition_code,
    src.FINANCIAL_IMPACT_AMOUNT as financial_impact_amount,
    src.OUTCOME_AT as outcome_at,
    src.LOSS_AMOUNT as loss_amount,
    src.RECOVERED_AMOUNT as recovered_amount,
    src.WRITE_OFF_AMOUNT as write_off_amount,
    src.RECOVERY_STATUS_CODE as recovery_status_code,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'case_disposition') }} as src
{{ fraudlens_batch_where('src') }}
