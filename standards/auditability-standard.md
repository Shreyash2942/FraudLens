# Auditability Standard

## Required Audit Fields

Governed contracts should account for the following audit and trace fields, either directly or by inheritance into later physical models:

- `record_source`
- `source_record_id`
- `ingested_at`
- `effective_at`
- `created_at`
- `updated_at`
- `created_by`
- `updated_by`
- `change_reason_code`
- `lineage_run_id`

## Audit Principles

- timestamps should be recorded in UTC
- status changes must be reconstructable from event history or linked records
- alert, case, investigation, decision, and disposition lifecycles must remain traceable
- no business-critical record should rely on undocumented free-text status values

## Evidence Expectations

Future implementation phases should be able to answer:

- where did this record come from
- when did it change
- who or what changed it
- what approval model governed the change
- which downstream business objects depend on it
