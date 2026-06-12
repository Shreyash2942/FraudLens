{{ config(alias='bronze_stg_reference_data_catalog', tags=['bronze', 'staging_raw']) }}

select
    src.CODE_SET_NAME as code_set_name,
    src.CODE_VALUE as code_value,
    src.CODE_DESCRIPTION as code_description,
    src.IS_ACTIVE as is_active,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'reference_data_catalog') }} as src
{{ fraudlens_batch_where('src') }}
