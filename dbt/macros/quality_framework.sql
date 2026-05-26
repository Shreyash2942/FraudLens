{% macro fraudlens_quality_severity_levels() -%}
    {{ return(['critical', 'high', 'medium', 'low']) }}
{%- endmacro %}

{% macro fraudlens_quality_assert_non_empty(expr) -%}
    ({{ expr }} is not null and trim(cast({{ expr }} as string)) <> '')
{%- endmacro %}

{% macro fraudlens_quality_assert_between(expr, min_value, max_value) -%}
    ({{ expr }} between {{ min_value }} and {{ max_value }})
{%- endmacro %}

{% macro fraudlens_quality_assert_in(expr, allowed_values_csv) -%}
    (
        {{ expr }} in (
            {%- for value in allowed_values_csv.split(',') -%}
                '{{ value.strip() }}'{% if not loop.last %}, {% endif %}
            {%- endfor -%}
        )
    )
{%- endmacro %}

{% macro fraudlens_quality_critical_model_patterns() -%}
    {{ return([
        'stg_bronze__payment_instruction',
        'stg_bronze__payment_transaction',
        'stg_bronze__risk_signal',
        'stg_bronze__fraud_alert',
        'stg_bronze__fraud_case',
        'slv__payment_instruction',
        'slv__payment_transaction',
        'slv__risk_signal',
        'slv__fraud_alert',
        'slv__fraud_case',
        'fact_transactions',
        'fact_payment_events',
        'fact_fraud_alerts',
        'fact_daily_fraud_metrics',
        'kpi_daily_fraud_operations',
        'kpi_portfolio_risk_snapshot'
    ]) }}
{%- endmacro %}
