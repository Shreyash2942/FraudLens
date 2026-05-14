{{ config(alias='SILVER_REFERENCE_DATA_CATALOG', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.code_set_name') }} as code_set_name,
    {{ fraudlens_clean_text('src.code_value') }} as code_value,
    {{ fraudlens_clean_text('src.code_description') }} as code_description,
    {{ fraudlens_clean_boolean('src.is_active') }} as is_active,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__reference_data_catalog') }} as src
{{ fraudlens_batch_where('src') }}
