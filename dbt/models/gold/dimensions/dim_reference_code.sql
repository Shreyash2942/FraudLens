{{ config(alias='gold_dim_reference_code', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['rc.code_set_name', 'rc.code_value']) }} as dim_reference_code_sk,
    rc.code_set_name,
    rc.code_value,
    rc.code_description,
    rc.is_active,
    rc.ingestion_batch_id,
    rc.source_file_name,
    rc.ingested_at_utc,
    rc.pipeline_processed_at_utc,
    rc.lineage_run_id
from {{ ref('slv__reference_data_catalog') }} as rc
