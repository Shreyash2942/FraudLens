{{ config(alias='SILVER_CHANNEL_EVENT', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.channel_event_id') }} as channel_event_id,
    {{ fraudlens_clean_text('src.channel_code', uppercase=true) }} as channel_code,
    {{ fraudlens_clean_text('src.session_id') }} as session_id,
    {{ fraudlens_clean_text('src.branch_id') }} as branch_id,
    {{ fraudlens_clean_timestamp('src.event_at') }} as event_at,
    {{ fraudlens_clean_text('src.event_country_code', uppercase=true) }} as event_country_code,
    {{ fraudlens_clean_text('src.ip_country_code', uppercase=true) }} as ip_country_code,
    {{ fraudlens_clean_text('src.authentication_result_code', uppercase=true) }} as authentication_result_code,
    {{ fraudlens_clean_text('src.session_risk_code', uppercase=true) }} as session_risk_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__channel_event') }} as src
{{ fraudlens_batch_where('src') }}
