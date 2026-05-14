{{ config(alias='SILVER_DEVICE_PROFILE', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.device_id') }} as device_id,
    {{ fraudlens_clean_text('src.device_status', uppercase=true) }} as device_status,
    {{ fraudlens_clean_text('src.operating_system_code', uppercase=true) }} as operating_system_code,
    {{ fraudlens_clean_text('src.device_risk_band', uppercase=true) }} as device_risk_band,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__device_profile') }} as src
{{ fraudlens_batch_where('src') }}
