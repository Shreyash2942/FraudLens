# Phase 5 Critical Dataset Rule Matrix

## Purpose

This matrix defines critical validation categories, control priorities, and acceptance targets for core FraudLens datasets and serving models.

## Severity Legend

- `C` = critical (hard block)
- `H` = high (readiness block)
- `M` = medium (must resolve before signoff)
- `L` = low (monitoring)

## Matrix

| Dataset / Model Family | Layer | Completeness | Uniqueness | Relationships | Accepted Values | Audit Traceability | Reconciliation | Notes |
|---|---|---|---|---|---|---|---|---|
| payment_instruction | Bronze | C | C | H | H | C | H | payment lifecycle anchor |
| payment_transaction | Bronze | C | C | H | H | C | H | execution events |
| risk_signal | Bronze | C | C | H | H | C | M | risk evidence source |
| fraud_alert | Bronze | C | C | H | H | C | M | alert lifecycle start |
| fraud_case | Bronze | C | C | H | H | C | M | case lifecycle anchor |
| payment_instruction | Silver | C | C | C | H | C | M | canonical payer/payee path |
| payment_transaction | Silver | C | C | C | H | C | M | canonical execution grain |
| risk_signal | Silver | C | C | C | H | C | M | risk conformance |
| fraud_alert | Silver | C | C | C | H | C | M | alert conformance |
| fraud_case | Silver | C | C | C | H | C | M | case conformance |
| decision_record | Silver | C | C | C | H | C | M | adjudication controls |
| case_disposition | Silver | C | C | C | H | C | M | closure controls |
| fact_transactions | Gold | C | C | C | H | C | H | transaction serving fact |
| fact_payment_events | Gold | C | C | C | H | C | H | payment event serving fact |
| fact_fraud_alerts | Gold | C | C | C | H | C | H | alert serving fact |
| fact_daily_fraud_metrics | Gold | C | C | H | H | C | H | daily aggregation trust |
| key dimensions (customer/account/card/date/region/org) | Gold | C | C | C | M | H | M | slicing/filtering consistency |
| kpi_daily_fraud_operations | Gold KPI | C | C | H | C | C | H | operational KPI trust |
| kpi_portfolio_risk_snapshot | Gold KPI | C | C | H | C | C | H | portfolio KPI trust |

## Category Expectations

### Completeness (`not_null`)
- enforced at critical key fields and required control fields
- critical model failures are hard-stop

### Uniqueness (`unique`)
- enforced on contract-defined unique keys and serving grains
- duplicate detections on critical models are hard-stop

### Relationships (`relationships`)
- aligned with `specs/relationship-map.yaml`
- critical relationship breaks are hard-stop

### Accepted Values (`accepted_values`)
- controlled fields include status/severity/type/decision/disposition domains
- priority is highest on lifecycle-driving fields

### Audit Traceability
- required audit lineage fields must remain present and non-null for critical outputs
- includes batch and run identifiers for trace continuity

### Reconciliation
- strict parity where one-to-one interface is expected
- documented tolerances where aggregation or deduplication is intentional

## Acceptance Threshold Baseline

- critical null tolerance: `0%`
- critical duplicate tolerance: `0%`
- critical relationship failure tolerance: `0%`
- critical KPI out-of-range tolerance: `0%`
- controlled-value violation tolerance on critical fields: `0%`

## Control Priority Guidance

Execution order in strict validation mode:
1. completeness + uniqueness on critical models
2. critical relationships
3. audit traceability checks
4. accepted values on critical lifecycle fields
5. reconciliation controls
