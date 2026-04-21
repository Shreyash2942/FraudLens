# Modeling Standard

## Source Of Truth

Structured contracts in `specs/` are the primary design source of truth. Narrative Markdown supports the model but does not replace contracts.

## Required Contract Sections

Every governed entity contract should include:

- entity metadata
- business description
- standards alignment
- ownership and stewardship
- keys and relationships
- control classification
- lineage intent
- required audit columns
- field-level metadata

## Modeling Rules

- payment and transaction entities should be ISO 20022-inspired in semantic meaning
- domains should be grouped using BIAN-inspired business boundaries where practical
- fraud operations entities should model alerting and case management as first-class business objects
- business identifiers must be stable and human-reviewable
- relationships must support later star-schema and medallion implementations without redefining the business object

## Field Metadata Requirements

Each field should define:

- name
- type
- description
- nullability
- semantic role
- example or allowed values when useful

## Critical Entity Classification

Entities that influence financial exposure, fraud decisions, or reported KPIs should be marked as `critical` and must carry explicit control metadata.
