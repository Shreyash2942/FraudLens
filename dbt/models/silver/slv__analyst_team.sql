{{ config(alias='SILVER_ANALYST_TEAM', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.analyst_team_id') }} as analyst_team_id,
    {{ fraudlens_clean_text('src.analyst_team_code', uppercase=true) }} as analyst_team_code,
    {{ fraudlens_clean_text('src.analyst_team_name') }} as analyst_team_name,
    {{ fraudlens_clean_text('src.business_unit_id') }} as business_unit_id,
    {{ fraudlens_clean_text('src.region_id') }} as region_id,
    {{ fraudlens_clean_boolean('src.is_active') }} as is_active,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__analyst_team') }} as src
{{ fraudlens_batch_where('src') }}
