{{ config(alias='GOLD_FACT_PAYMENT_EVENTS', tags=['gold', 'fact']) }}

with payment_instructions as (
    select *
    from {{ ref('slv__payment_instruction') }}
),
transaction_rollup as (
    select
        pt.payment_instruction_id,
        count(pt.payment_transaction_id) as payment_transaction_count,
        sum(case when pt.transaction_status = 'SETTLED' then 1 else 0 end) as settled_transaction_count,
        sum(case when pt.transaction_status = 'REVERSED' or pt.reversal_reason_code is not null then 1 else 0 end) as reversed_transaction_count,
        sum(coalesce(pt.booking_amount, 0)) as total_booking_amount,
        sum(case when pt.transaction_status = 'SETTLED' then coalesce(pt.booking_amount, 0) else 0 end) as settled_booking_amount,
        min(pt.settlement_at) as first_settlement_at,
        max(pt.settlement_at) as latest_settlement_at
    from {{ ref('slv__payment_transaction') }} as pt
    group by pt.payment_instruction_id
),
risk_rollup as (
    select
        rs.payment_instruction_id,
        count(rs.risk_signal_id) as risk_signal_count,
        sum(case when rs.risk_level in ('HIGH', 'CRITICAL') then 1 else 0 end) as high_risk_signal_count,
        max(rs.signal_score_amount) as max_signal_score_amount,
        min(rs.event_at) as first_risk_event_at
    from {{ ref('slv__risk_signal') }} as rs
    group by rs.payment_instruction_id
),
alert_rollup as (
    select
        rs.payment_instruction_id,
        count(fa.fraud_alert_id) as fraud_alert_count,
        sum(case when fa.alert_severity in ('HIGH', 'CRITICAL') then 1 else 0 end) as high_severity_alert_count,
        sum(case when fa.alert_status in ('OPEN', 'NEW', 'IN_PROGRESS', 'ESCALATED') then 1 else 0 end) as open_alert_count,
        min(fa.created_at) as first_alert_created_at
    from {{ ref('slv__risk_signal') }} as rs
    left join {{ ref('slv__fraud_alert') }} as fa
        on rs.risk_signal_id = fa.risk_signal_id
    group by rs.payment_instruction_id
),
case_rollup as (
    select
        rs.payment_instruction_id,
        count(fc.fraud_case_id) as fraud_case_count,
        sum(case when fc.case_status in ('OPEN', 'NEW', 'IN_PROGRESS', 'ESCALATED') then 1 else 0 end) as open_case_count,
        min(fc.opened_at) as first_case_opened_at
    from {{ ref('slv__risk_signal') }} as rs
    left join {{ ref('slv__fraud_alert') }} as fa
        on rs.risk_signal_id = fa.risk_signal_id
    left join {{ ref('slv__fraud_case') }} as fc
        on fa.fraud_alert_id = fc.primary_alert_id
    group by rs.payment_instruction_id
)
select
    {{ fraudlens_fact_sk(['pi.payment_instruction_id']) }} as fact_payment_event_sk,
    pi.payment_instruction_id,
    coalesce(to_date(pi.event_at), pi.booking_date) as payment_event_date,
    pi.event_at as payment_event_at,
    pi.booking_date,
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
    coalesce(tr.payment_transaction_count, 0) as payment_transaction_count,
    coalesce(tr.settled_transaction_count, 0) as settled_transaction_count,
    coalesce(tr.reversed_transaction_count, 0) as reversed_transaction_count,
    coalesce(tr.total_booking_amount, 0) as total_booking_amount,
    coalesce(tr.settled_booking_amount, 0) as settled_booking_amount,
    tr.first_settlement_at,
    tr.latest_settlement_at,
    coalesce(rr.risk_signal_count, 0) as risk_signal_count,
    coalesce(rr.high_risk_signal_count, 0) as high_risk_signal_count,
    coalesce(rr.max_signal_score_amount, 0) as max_signal_score_amount,
    rr.first_risk_event_at,
    coalesce(ar.fraud_alert_count, 0) as fraud_alert_count,
    coalesce(ar.high_severity_alert_count, 0) as high_severity_alert_count,
    coalesce(ar.open_alert_count, 0) as open_alert_count,
    ar.first_alert_created_at,
    coalesce(cr.fraud_case_count, 0) as fraud_case_count,
    coalesce(cr.open_case_count, 0) as open_case_count,
    cr.first_case_opened_at,
    case
        when pi.event_at is not null and ar.first_alert_created_at is not null then cast((unix_timestamp(ar.first_alert_created_at) - unix_timestamp(pi.event_at)) / 60 as int)
        else null
    end as minutes_to_first_alert,
    case
        when pi.event_at is not null and tr.first_settlement_at is not null then cast((unix_timestamp(tr.first_settlement_at) - unix_timestamp(pi.event_at)) / 60 as int)
        else null
    end as minutes_to_first_settlement,
    case
        when coalesce(rr.high_risk_signal_count, 0) > 0 or coalesce(ar.high_severity_alert_count, 0) > 0 then true
        else false
    end as is_high_risk_payment_event,
    pi.ingestion_batch_id,
    pi.source_file_name,
    pi.ingested_at_utc,
    pi.pipeline_processed_at_utc,
    pi.lineage_run_id
from payment_instructions as pi
left join transaction_rollup as tr
    on pi.payment_instruction_id = tr.payment_instruction_id
left join risk_rollup as rr
    on pi.payment_instruction_id = rr.payment_instruction_id
left join alert_rollup as ar
    on pi.payment_instruction_id = ar.payment_instruction_id
left join case_rollup as cr
    on pi.payment_instruction_id = cr.payment_instruction_id
