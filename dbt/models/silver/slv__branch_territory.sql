{{ config(alias='SILVER_BRANCH_TERRITORY', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.branch_territory_id') }} as branch_territory_id,
    {{ fraudlens_clean_text('src.branch_territory_code', uppercase=true) }} as branch_territory_code,
    {{ fraudlens_clean_text('src.branch_territory_name') }} as branch_territory_name,
    {{ fraudlens_clean_text('src.region_id') }} as region_id,
    {{ fraudlens_clean_boolean('src.is_active') }} as is_active,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__branch_territory') }} as src
{{ fraudlens_batch_where('src') }}
