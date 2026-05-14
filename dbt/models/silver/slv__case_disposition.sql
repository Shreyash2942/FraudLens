{{ config(alias='SILVER_CASE_DISPOSITION', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.disposition_id') }} as disposition_id,
    {{ fraudlens_clean_text('src.decision_id') }} as decision_id,
    {{ fraudlens_clean_text('src.disposition_code', uppercase=true) }} as disposition_code,
    {{ fraudlens_clean_decimal('src.financial_impact_amount') }} as financial_impact_amount,
    {{ fraudlens_clean_timestamp('src.outcome_at') }} as outcome_at,
    {{ fraudlens_clean_decimal('src.loss_amount') }} as loss_amount,
    {{ fraudlens_clean_decimal('src.recovered_amount') }} as recovered_amount,
    {{ fraudlens_clean_decimal('src.write_off_amount') }} as write_off_amount,
    {{ fraudlens_clean_text('src.recovery_status_code', uppercase=true) }} as recovery_status_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__case_disposition') }} as src
{{ fraudlens_batch_where('src') }}
