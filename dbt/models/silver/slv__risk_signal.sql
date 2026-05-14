{{ config(alias='SILVER_RISK_SIGNAL', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.risk_signal_id') }} as risk_signal_id,
    {{ fraudlens_clean_text('src.payment_instruction_id') }} as payment_instruction_id,
    {{ fraudlens_clean_text('src.signal_type_code', uppercase=true) }} as signal_type_code,
    {{ fraudlens_clean_decimal('src.signal_score_amount') }} as signal_score_amount,
    {{ fraudlens_clean_text('src.risk_level', uppercase=true) }} as risk_level,
    {{ fraudlens_clean_timestamp('src.event_at') }} as event_at,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__risk_signal') }} as src
{{ fraudlens_batch_where('src') }}
