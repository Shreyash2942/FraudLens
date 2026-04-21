# Naming Conventions

## Repository Conventions

- technical folders use conventional lowercase names
- business contracts use snake_case entity names
- version folders use `v1`, `v2`, and so on

## Business Naming Conventions

- use business-domain names inspired by BIAN service-domain thinking
- keep dataset names stable across raw, transformed, and BI representations
- prefer explicit names such as `payment_instruction`, `fraud_alert`, and `case_disposition`
- avoid vague names such as `txn_data`, `master_table`, or `generic_alert`

## Field Naming

- primary keys end with `_id`
- foreign keys reuse the referenced business identifier
- UTC timestamps end with `_at`
- dates use `_date`
- monetary amounts use `_amount`
- currency codes use `_currency_code`
- status fields use `_status`
- boolean flags use `is_` or `has_`

## Status Values

- statuses should be enumerated in reference contracts or field metadata
- statuses must represent business lifecycle state, not technical pipeline state
