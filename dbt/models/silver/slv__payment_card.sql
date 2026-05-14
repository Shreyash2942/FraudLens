{{ config(alias='SILVER_PAYMENT_CARD', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.card_id') }} as card_id,
    {{ fraudlens_clean_text('src.linked_account_id') }} as linked_account_id,
    {{ fraudlens_clean_text('src.card_status', uppercase=true) }} as card_status,
    {{ fraudlens_clean_text('src.card_network_code', uppercase=true) }} as card_network_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__payment_card') }} as src
{{ fraudlens_batch_where('src') }}
