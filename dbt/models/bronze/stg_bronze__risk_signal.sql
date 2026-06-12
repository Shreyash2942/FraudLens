{{ config(alias='bronze_stg_risk_signal', tags=['bronze', 'staging_raw']) }}

select
    src.RISK_SIGNAL_ID as risk_signal_id,
    src.PAYMENT_INSTRUCTION_ID as payment_instruction_id,
    src.SIGNAL_TYPE_CODE as signal_type_code,
    src.SIGNAL_SCORE_AMOUNT as signal_score_amount,
    src.RISK_LEVEL as risk_level,
    src.EVENT_AT as event_at,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'risk_signal') }} as src
{{ fraudlens_batch_where('src') }}
