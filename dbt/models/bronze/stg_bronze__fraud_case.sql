{{ config(alias='BRONZE_STG_FRAUD_CASE', tags=['bronze', 'staging_raw']) }}

select
    src.FRAUD_CASE_ID as fraud_case_id,
    src.PRIMARY_ALERT_ID as primary_alert_id,
    src.CASE_STATUS as case_status,
    src.ASSIGNED_ANALYST_PARTY_ID as assigned_analyst_party_id,
    src.OPENED_AT as opened_at,
    src.CLOSED_AT as closed_at,
    src.CASE_TYPE_CODE as case_type_code,
    src.CASE_PRIORITY_CODE as case_priority_code,
    src.OWNING_BUSINESS_UNIT_ID as owning_business_unit_id,
    src.OWNING_ANALYST_TEAM_ID as owning_analyst_team_id,
    src.HANDLING_REGION_ID as handling_region_id,
    src.ESCALATION_LEVEL_CODE as escalation_level_code,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'fraud_case') }} as src
{{ fraudlens_batch_where('src') }}
