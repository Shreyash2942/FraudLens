{{ config(alias='SILVER_BRANCH_LOCATION', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.branch_id') }} as branch_id,
    {{ fraudlens_clean_text('src.branch_code', uppercase=true) }} as branch_code,
    {{ fraudlens_clean_text('src.branch_name') }} as branch_name,
    {{ fraudlens_clean_text('src.branch_territory_id') }} as branch_territory_id,
    {{ fraudlens_clean_text('src.region_id') }} as region_id,
    {{ fraudlens_clean_text('src.country_code', uppercase=true) }} as country_code,
    {{ fraudlens_clean_text('src.city_name') }} as city_name,
    {{ fraudlens_clean_boolean('src.is_active') }} as is_active,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__branch_location') }} as src
{{ fraudlens_batch_where('src') }}
