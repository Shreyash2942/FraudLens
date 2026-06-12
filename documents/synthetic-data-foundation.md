# Synthetic Data Foundation (Phase 2)

Status date: `2026-05-25`
Milestone scope: `#29` with sub-issues `#30`-`#37`

## Purpose

This document consolidates Phase 2 design and delivery planning into one implementation and review artifact.

## Primary Phase File

Use this as the primary Phase 2 review and handoff file in `documents/`.

## Scope Consolidated

- `#30` Define dataset architecture and relationships
- `#31` Design core dataset schemas
- `#32` Design extended and reference datasets
- `#33` Implement data generator (Python)
- `#34` Add fraud simulation logic
- `#35` Export and structure data files
- `#36` Load data into object storage (MinIO)
- `#37` Validate data integrity and relationships

## Executive Outcome

Phase 2 established a deterministic synthetic data foundation aligned to FraudLens domain and governance standards:

- 21 governed datasets spanning banking, payment, fraud operations, and dashboard dimensions
- ISO 20022-inspired transaction/account/payment semantics
- BIAN-inspired domain grouping across entities and flows
- fraud operations entities for alerts, cases, investigations, decisions, and dispositions
- reproducible batch generation with blueprint support and scale profiles
- local-first output layout under `data/batches/<batch_id>/` with optional MinIO upload
- validation contracts for structural and relationship integrity

## Data Product Design

### Dataset Families

- Core and master data: customer, account, card, branch, merchant, device, and supporting references
- Calendar/geography/organization dimensions for dashboard slicing and regional governance
- Transactional datasets for payment and account activity analysis
- Fraud operations datasets for risk alerting, case lifecycle, and investigative outcomes

### Modeling Position

- canonical identifiers and cross-entity link keys are preserved for downstream joins
- business-safe typed fields and controlled enumerations are defined for core entities
- relationship assumptions align with `specs/relationship-map.yaml`

### Behavioral Simulation

- fraud scenarios are deterministic within a run context for repeatable testing
- scenario injection supports lifecycle progression from risk signals to case outcomes
- behavioral distributions are configurable through profile and blueprint inputs

## Runtime and Interfaces

### CLI and Batch Behavior

- governed generator entrypoints support seeded deterministic runs
- batch artifact manifests and dataset metadata are emitted per run
- profile-based generation supports `small_fast` and `medium_demo` execution modes

### Output Artifacts

- local outputs are written to `data/batches/<batch_id>/`
- structured files are generated for Bronze ingestion and contract validation
- optional MinIO upload flow mirrors local batch structure for warehouse loading

## Governance and Validation

- required fields, type assumptions, and relationship checks are validated during generation and post-run validation
- generated outputs are contract-aware and designed for Bronze compatibility
- phase acceptance requires deterministic reruns and integrity checks on key relationships

## Delivery Plan Alignment

The GitHub issue pack for Phase 2 maps the milestone into one epic with eight sub-issues and reusable issue bodies, including acceptance criteria and references for each workstream.

## Consolidation Note

Earlier Phase 2 working documents were consolidated into this file and are not retained separately
in the root `documents/` directory.

## Reviewer Notes

Use this as the only retained Phase 2 document in `documents/`.
