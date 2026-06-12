{{ config(alias='gold_fact_transactions', tags=['gold', 'fact'], materialized='incremental') }}

with transactions as (
    select *
    from {{ ref('slv__payment_transaction') }}
    {% if is_incremental() and var('fraudlens_batch_id', '') | length > 0 %}
    where ingestion_batch_id = '{{ var("fraudlens_batch_id") }}'
    {% endif %}
),
payment_instructions as (
    select *
    from {{ ref('slv__payment_instruction') }}
),
risk_rollup as (
    select
        rs.payment_instruction_id,
        count(rs.risk_signal_id) as risk_signal_count,
        sum(case when rs.risk_level in ('HIGH', 'CRITICAL') then 1 else 0 end) as high_risk_signal_count,
        max(rs.signal_score_amount) as max_signal_score_amount
    from {{ ref('slv__risk_signal') }} as rs
    group by rs.payment_instruction_id
),
alert_rollup as (
    select
        rs.payment_instruction_id,
        count(fa.fraud_alert_id) as fraud_alert_count,
        sum(case when fa.alert_severity in ('HIGH', 'CRITICAL') then 1 else 0 end) as high_severity_alert_count,
        sum(case when fa.alert_status in ('OPEN', 'NEW', 'IN_PROGRESS', 'ESCALATED') then 1 else 0 end) as open_alert_count
    from {{ ref('slv__risk_signal') }} as rs
    left join {{ ref('slv__fraud_alert') }} as fa
        on rs.risk_signal_id = fa.risk_signal_id
    group by rs.payment_instruction_id
),
case_rollup as (
    select
        rs.payment_instruction_id,
        count(fc.fraud_case_id) as fraud_case_count,
        sum(case when fc.case_status in ('OPEN', 'NEW', 'IN_PROGRESS', 'ESCALATED') then 1 else 0 end) as open_case_count
    from {{ ref('slv__risk_signal') }} as rs
    left join {{ ref('slv__fraud_alert') }} as fa
        on rs.risk_signal_id = fa.risk_signal_id
    left join {{ ref('slv__fraud_case') }} as fc
        on fa.fraud_alert_id = fc.primary_alert_id
    group by rs.payment_instruction_id
)
select
    {{ fraudlens_fact_sk(['tx.payment_transaction_id', 'tx.payment_instruction_id']) }} as fact_transaction_sk,
    tx.payment_transaction_id,
    tx.payment_instruction_id,
    coalesce(tx.posted_date, tx.value_date, to_date(tx.settlement_at), pi.booking_date) as transaction_date,
    tx.posted_date,
    tx.value_date,
    tx.settlement_at,
    tx.transaction_status,
    tx.transaction_direction_code,
    tx.transaction_currency_code,
    tx.booking_amount,
    tx.reversal_reason_code,
    case
        when tx.transaction_status = 'REVERSED' or tx.reversal_reason_code is not null then true
        else false
    end as is_reversal,
    tx.merchant_category_code,
    pi.instruction_status,
    pi.instructed_amount,
    pi.instructed_currency_code,
    pi.payment_rail_code,
    pi.payment_purpose_code,
    pi.is_cross_border,
    pi.merchant_country_code,
    pi.counterparty_bank_country_code,
    pi.debtor_account_id,
    pi.debtor_party_id,
    pi.creditor_party_id,
    pi.channel_event_id,
    pi.card_id,
    pi.device_id,
    coalesce(rr.risk_signal_count, 0) as risk_signal_count,
    coalesce(rr.high_risk_signal_count, 0) as high_risk_signal_count,
    coalesce(rr.max_signal_score_amount, 0) as max_signal_score_amount,
    coalesce(ar.fraud_alert_count, 0) as fraud_alert_count,
    coalesce(ar.high_severity_alert_count, 0) as high_severity_alert_count,
    coalesce(ar.open_alert_count, 0) as open_alert_count,
    coalesce(cr.fraud_case_count, 0) as fraud_case_count,
    coalesce(cr.open_case_count, 0) as open_case_count,
    coalesce(tx.ingestion_batch_id, pi.ingestion_batch_id) as ingestion_batch_id,
    coalesce(tx.source_file_name, pi.source_file_name) as source_file_name,
    coalesce(tx.ingested_at_utc, pi.ingested_at_utc) as ingested_at_utc,
    coalesce(
        tx.created_at_utc,
        pi.created_at_utc,
        tx.settlement_at,
        pi.event_at,
        tx.ingested_at_utc,
        pi.ingested_at_utc
    ) as created_at_utc,
    coalesce(
        tx.updated_at_utc,
        pi.updated_at_utc,
        tx.pipeline_processed_at_utc,
        pi.pipeline_processed_at_utc
    ) as updated_at_utc,
    coalesce(tx.source_system, pi.source_system, 'synthetic_generator') as source_system,
    coalesce(tx.pipeline_run_id, pi.pipeline_run_id, tx.lineage_run_id, pi.lineage_run_id) as pipeline_run_id,
    coalesce(tx.pipeline_processed_at_utc, pi.pipeline_processed_at_utc) as pipeline_processed_at_utc,
    coalesce(tx.lineage_run_id, pi.lineage_run_id) as lineage_run_id
from transactions as tx
left join payment_instructions as pi
    on tx.payment_instruction_id = pi.payment_instruction_id
left join risk_rollup as rr
    on tx.payment_instruction_id = rr.payment_instruction_id
left join alert_rollup as ar
    on tx.payment_instruction_id = ar.payment_instruction_id
left join case_rollup as cr
    on tx.payment_instruction_id = cr.payment_instruction_id
