{{ config(alias='GOLD_DIM_DEVICE', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['dp.device_id']) }} as dim_device_sk,
    dp.device_id,
    dp.device_status,
    dp.operating_system_code,
    dp.device_risk_band,
    dp.ingestion_batch_id,
    dp.source_file_name,
    dp.ingested_at_utc,
    dp.pipeline_processed_at_utc,
    dp.lineage_run_id
from {{ ref('slv__device_profile') }} as dp
