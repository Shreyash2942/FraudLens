{{ config(alias='bronze_stg_decision_record', tags=['bronze', 'staging_raw']) }}

select
    src.DECISION_ID as decision_id,
    src.FRAUD_CASE_ID as fraud_case_id,
    src.DECISION_TYPE as decision_type,
    src.DECISION_STATUS as decision_status,
    src.DECISION_MAKER_PARTY_ID as decision_maker_party_id,
    src.DECIDED_AT as decided_at,
    src.DECISION_REASON_CODE as decision_reason_code,
    src.DECISION_CHANNEL_CODE as decision_channel_code,
    src.POLICY_NAME as policy_name,
    src.RULE_SET_VERSION as rule_set_version,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'decision_record') }} as src
{{ fraudlens_batch_where('src') }}
