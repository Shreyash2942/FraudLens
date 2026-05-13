{{ config(alias='BRONZE_STG_PARTY_ORG_ASSIGNMENT', tags=['bronze', 'staging_raw']) }}

select
    src.PARTY_ORG_ASSIGNMENT_ID as party_org_assignment_id,
    src.PARTY_ID as party_id,
    src.BUSINESS_UNIT_ID as business_unit_id,
    src.ANALYST_TEAM_ID as analyst_team_id,
    src.BRANCH_ID as branch_id,
    src.ASSIGNMENT_ROLE_CODE as assignment_role_code,
    src.EFFECTIVE_FROM_AT as effective_from_at,
    src.EFFECTIVE_TO_AT as effective_to_at,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'party_org_assignment') }} as src
{{ fraudlens_batch_where('src') }}
