# FraudLens Phase 2 GitHub Issue Pack

This document provides GitHub-ready issue text for the FraudLens Phase 2 milestone.

Use this issue pack when creating or backfilling GitHub issues for:

- milestone: `Phase 2 - Dataset And Data Design`
- labels: `phase:2`

Recommended structure:

1. create the Phase 2 epic issue first
2. create the task issues under the same milestone
3. link each task back to the epic in GitHub

---

## Epic

### Title

`Phase 2 - Dataset And Data Design`

### Labels

- `phase:2`
- `type:epic`
- `area:data`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Implement the FraudLens Phase 2 synthetic data foundation so the governed banking and fraud model is available as deterministic, testable, physical datasets for downstream warehouse, transformation, and analytics work.

## Goals

- turn the governed Phase 2 contracts into generated physical datasets
- support realistic fraud analytics and fraud-operations scenarios
- keep outputs reproducible through deterministic seed-based generation
- produce control, manifest, and validation artifacts alongside dataset exports
- support local object-storage handoff through optional MinIO upload

## Scope

- 21 generated datasets spanning core banking, fraud operations, calendar, geography, and organization dimensions
- mixed generation mode for broad synthetic coverage
- blueprint mode for curated fraud-ops showcase runs
- validation reporting for integrity, temporal consistency, behavioral consistency, org consistency, and blueprint compliance
- batch-style export layout under `data/batches/<batch_id>/`

## Out Of Scope

- warehouse schema implementation
- Bronze, Silver, and Gold transformations
- production orchestration
- BI dashboards

## Acceptance Criteria

- 21 governed datasets are generated in a deterministic and repeatable way
- outputs are written into landing, control, and quality areas
- the generator supports both mixed and blueprint-driven runs
- validation reporting is produced when requested
- optional MinIO upload is supported through local configuration
- Phase 2 documentation and smoke-test coverage exist in the repository

## Child Issues

- Govern the Phase 2 dataset inventory and domain contract alignment
- Build the deterministic synthetic generator CLI and planning flow
- Export all Phase 2 datasets with batch control artifacts
- Model fraud lifecycle behavior and dashboard control dimensions
- Add curated blueprint support for showcase fraud-ops batches
- Add validation and compliance checks for generated batches
- Add optional MinIO upload support for generated artifacts
- Add Phase 2 smoke tests and usage documentation

## References

- `documents/implementation-roadmap.md`
- `documents/phase-2-dataset-design.md`
- `synthetic_generator/README.md`
- `tests/test_phase2_generator.py`
```

---

## Task 1

### Title

`Govern the Phase 2 dataset inventory and domain contract alignment`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `area:governance`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Confirm that the Phase 2 generator targets the current governed dataset inventory and aligns to the structured contracts in `specs/`.

## Scope

- use the YAML contracts in `specs/` as the design source of truth
- align the generator to the expanded 21-dataset model
- preserve ISO 20022-inspired semantics for payments and accounts
- preserve BIAN-inspired business-domain grouping
- include fraud-ops entities for risk, alerts, cases, investigations, decisions, and dispositions
- include calendar, geography, and organization dimensions for dashboard control

## Acceptance Criteria

- the implemented dataset set covers all 21 governed outputs
- dataset naming is consistent across code, docs, and generated artifacts
- Phase 2 documentation explicitly reflects the current governed model
- the repo no longer relies on the outdated 10-dataset framing

## References

- `documents/phase-2-dataset-design.md`
- `specs/`
- `synthetic_generator/contracts.py`
```

---

## Task 2

### Title

`Build the deterministic synthetic generator CLI and planning flow`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Implement the Phase 2 synthetic generator entry point, deterministic planning behavior, and reproducible run controls.

## Scope

- provide a CLI entry point for mixed and blueprint generation modes
- support deterministic seed-based generation
- support configurable duration and scale profiles
- use seeded Faker-backed realism where helpful
- produce stable batch identifiers and run metadata

## Acceptance Criteria

- the generator runs from the repository root via `py -m synthetic_generator.generate`
- deterministic inputs produce reproducible dataset outputs
- supported profiles include local-friendly and demo-friendly scales
- blueprint mode enforces blueprint selection
- built-in blueprints can be listed from the CLI

## References

- `synthetic_generator/generate.py`
- `synthetic_generator/planner.py`
- `synthetic_generator/realism.py`
- `synthetic_generator/README.md`
```

---

## Task 3

### Title

`Export all Phase 2 datasets with batch control artifacts`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Write the generated Phase 2 datasets to a governed batch layout and emit the control artifacts required for downstream ingestion and run traceability.

## Scope

- export 21 CSV datasets into batch-oriented landing storage
- emit a manifest with row counts, mode details, and scenario summaries
- emit batch control metadata with stage-level execution information
- keep generator code separate from generated output data

## Acceptance Criteria

- generated datasets land under `data/batches/<batch_id>/landing/csv/`
- `control/manifest.json` is written for every run
- `control/batch_control.json` is written for every run
- dataset row counts and dataset inventory are reflected in the manifest
- batch outputs are usable by later ingestion and warehouse phases

## References

- `synthetic_generator/exporter.py`
- `synthetic_generator/generate.py`
- `synthetic_generator/contracts.py`
- `synthetic_generator/README.md`
```

---

## Task 4

### Title

`Model fraud lifecycle behavior and dashboard control dimensions`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Generate realistic banking activity, fraud scenarios, fraud-operations lifecycle records, and supporting org/calendar dimensions needed for analytics and dashboard control.

## Scope

- model baseline account, payment, device, and channel behavior
- generate fraud scenarios such as account takeover, mule activity, card-not-present, and false-positive review
- generate risk, alert, case, investigation, decision, and disposition lifecycle records
- generate calendar, region, branch territory, branch location, business unit, analyst team, and party assignment dimensions

## Acceptance Criteria

- generated outputs include both banking behavior and fraud-ops lifecycle data
- organization and geography dimensions support ownership-based reporting
- calendar outputs support month, quarter, and trend slicing
- manifests summarize scenario outcomes and org/geography mixes

## References

- `synthetic_generator/behavior.py`
- `synthetic_generator/fraud.py`
- `synthetic_generator/state.py`
- `documents/phase-2-dataset-design.md`
```

---

## Task 5

### Title

`Add curated blueprint support for showcase fraud-ops batches`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `priority:p2`
- `status:ready`

### Body

```md
## Summary

Support curated blueprint-driven runs that shape fraud scenarios and lifecycle outcomes for repeatable showcase and demo batches.

## Scope

- add YAML-driven blueprint loading
- support built-in showcase blueprints
- support custom local blueprint files
- allow blueprint controls for scenario counts, timing, lifecycle targets, mixes, and realism settings

## Acceptance Criteria

- built-in blueprints can be listed and loaded successfully
- blueprint mode supports both built-in names and file-based blueprints
- blueprint runs include blueprint metadata in manifest and batch control outputs
- blueprint-specific targets influence scenario and lifecycle generation

## References

- `synthetic_generator/blueprints.py`
- `synthetic_generator/blueprints/`
- `synthetic_generator/planner.py`
- `synthetic_generator/README.md`
```

---

## Task 6

### Title

`Add validation and compliance checks for generated batches`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `area:governance`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Add post-generation quality validation so every Phase 2 batch can be checked for integrity, consistency, and blueprint compliance.

## Scope

- validate temporal consistency across generated events
- validate behavioral consistency across generated entities and activity
- validate organization-structure consistency
- validate blueprint compliance for blueprint-mode runs
- persist a machine-readable validation report

## Acceptance Criteria

- `quality/validation_report.json` is written when validation is requested
- validation status is reflected in the manifest
- failures are captured with actionable errors
- blueprint runs include blueprint compliance results

## References

- `synthetic_generator/validation.py`
- `synthetic_generator/generate.py`
- `tests/test_phase2_generator.py`
```

---

## Task 7

### Title

`Add optional MinIO upload support for generated artifacts`

### Labels

- `phase:2`
- `type:task`
- `area:platform`
- `area:data`
- `priority:p2`
- `status:ready`

### Body

```md
## Summary

Allow Phase 2 batch outputs to be uploaded to the local object-storage sandbox so downstream ingestion and platform integration flows can consume generated artifacts without manual copying.

## Scope

- add an optional upload flag to the generator CLI
- integrate with the local MinIO-compatible object storage contract
- publish generated artifacts under a consistent Phase 2 object path

## Acceptance Criteria

- MinIO upload is optional and does not block local generation when unused
- uploaded artifacts follow the expected Phase 2 storage path
- upload behavior is documented as part of the generator workflow

## References

- `synthetic_generator/storage.py`
- `synthetic_generator/generate.py`
- `documents/platform-foundation-guide.md`
```

---

## Task 8

### Title

`Add Phase 2 smoke tests and usage documentation`

### Labels

- `phase:2`
- `type:task`
- `area:data`
- `type:docs`
- `priority:p1`
- `status:ready`

### Body

```md
## Summary

Add enough automated verification and operator documentation to make the Phase 2 generator understandable, runnable, and reviewable.

## Scope

- add smoke tests for mixed mode and blueprint mode
- verify built-in blueprint discovery and loading
- document CLI usage and output layout
- document Phase 2 design intent and generated dataset coverage

## Acceptance Criteria

- test coverage exists for at least one mixed-mode and one blueprint-mode run
- documentation explains how to run the generator and interpret outputs
- documentation explains why the dataset inventory is 21 datasets
- custom blueprint usage is documented

## References

- `tests/test_phase2_generator.py`
- `synthetic_generator/README.md`
- `documents/phase-2-dataset-design.md`
```

---

## Copy-Paste Sub-Issue Bodies For Existing GitHub Issues

Use the following Markdown blocks directly in your current GitHub sub-issues `#30` to `#37`.

### #30 Define Dataset Architecture & Relationships

```md
## 🔵 Phase 2 — Define Dataset Architecture & Relationships

### 📌 Description
Define the governed Phase 2 dataset architecture and relationship model for FraudLens. This work establishes how the synthetic data foundation maps banking entities, fraud operations entities, and dashboard-control dimensions into a coherent relational model.

### 🎯 Objectives
- align the dataset model to the governed contracts in `specs/`
- define entity relationships across customer, account, payment, fraud, investigation, and decision domains
- establish primary-key and foreign-key structure
- preserve ISO 20022-inspired semantics and BIAN-inspired domain grouping
- support downstream warehouse ingestion and analytics design

### 🧩 Scope
- core banking entities
- payment and transaction entities
- fraud operations entities
- calendar, geography, and organization dimensions
- relationship mapping between operational and dimensional datasets

### ✅ Acceptance Criteria
- all governed Phase 2 datasets are represented in the architecture
- key relationships are clearly defined across all datasets
- primary and foreign keys are identified consistently
- the architecture supports downstream Bronze, Silver, Gold, and star-schema work
- documentation reflects the current governed model

### 📦 Expected Outcome
A documented relational architecture for the full Phase 2 dataset foundation, ready for generator implementation and downstream ingestion design.

### 🔗 References
- `documents/phase-2-dataset-design.md`
- `specs/`
- `synthetic_generator/contracts.py`
```

### #31 Design Core Dataset Schemas

```md
## 🔵 Phase 2 — Design Core Dataset Schemas

### 📌 Description
Design the core Phase 2 schemas for the primary banking and fraud operations entities used throughout the FraudLens synthetic generator and downstream analytics layers.

### 🎯 Objectives
- define governed schema structures for core entities
- standardize field naming, key structure, and traceability fields
- ensure schemas support realistic operational workflows
- keep the model compatible with warehouse and analytics use cases

### 🧩 Scope
- `party`
- `deposit_account`
- `payment_card`
- `device_profile`
- `channel_event`
- `payment_instruction`
- `payment_transaction`
- `risk_signal`
- `fraud_alert`
- `fraud_case`
- `investigation_event`
- `decision_record`
- `case_disposition`

### ✅ Acceptance Criteria
- each core dataset has a clearly defined schema and purpose
- key fields and relationship fields are documented
- schemas reflect realistic banking and fraud-ops semantics
- the generator can produce these datasets consistently

### 📦 Expected Outcome
A stable set of core Phase 2 dataset schemas that represent the operational backbone of FraudLens.

### 🔗 References
- `documents/phase-2-dataset-design.md`
- `specs/`
- `synthetic_generator/contracts.py`
```

### #32 Design Extended & Reference Datasets

```md
## 🔵 Phase 2 — Design Extended & Reference Datasets

### 📌 Description
Design the supporting datasets required for realistic reporting, dashboard slicing, ownership modeling, and reference-data control in the Phase 2 synthetic dataset foundation.

### 🎯 Objectives
- define supporting dimension and reference datasets
- support reporting by date, geography, branch, business unit, and analyst team
- provide realistic ownership and organizational context
- extend the Phase 2 model beyond the older 10-dataset baseline

### 🧩 Scope
- `reference_data_catalog`
- `calendar_day`
- `region`
- `branch_territory`
- `branch_location`
- `business_unit`
- `analyst_team`
- `party_org_assignment`

### ✅ Acceptance Criteria
- supporting datasets are modeled consistently with the core datasets
- organization and geography dimensions support dashboard control use cases
- calendar data supports trend and period reporting
- reference datasets integrate cleanly with generated transactional and fraud-ops outputs

### 📦 Expected Outcome
A complete supporting-dataset layer that makes the FraudLens Phase 2 model usable for management reporting, segmentation, and ownership-based analytics.

### 🔗 References
- `documents/phase-2-dataset-design.md`
- `specs/`
- `synthetic_generator/contracts.py`
```

### #33 Implement Data Generator (Python)

```md
## 🔵 Phase 2 — Implement Data Generator (Python)

### 📌 Description
Implement the Python-based synthetic data generator that creates deterministic Phase 2 batch outputs from the governed dataset model.

### 🎯 Objectives
- provide a CLI-driven generator
- support deterministic generation through seed-based execution
- support different run sizes and local-friendly profiles
- generate the full Phase 2 dataset inventory in batch form
- keep generation reproducible for testing and portfolio demonstrations

### 🧩 Scope
- generator CLI
- planning and run configuration
- deterministic seed handling
- scale profiles
- batch metadata
- mixed mode and blueprint mode support

### ✅ Acceptance Criteria
- generator runs from the repo root via `py -m synthetic_generator.generate`
- mixed mode produces a complete batch successfully
- blueprint mode is supported with valid blueprint input
- deterministic settings allow repeatable results
- generator outputs are organized under `data/batches/<batch_id>/`

### 📦 Expected Outcome
A functioning Python generator that produces governed synthetic Phase 2 batches for local development, testing, and downstream platform work.

### 🔗 References
- `synthetic_generator/generate.py`
- `synthetic_generator/planner.py`
- `synthetic_generator/README.md`
```

### #34 Add Fraud Simulation Logic

```md
## 🔵 Phase 2 — Add Fraud Simulation Logic

### 📌 Description
Add realistic fraud simulation behavior so the Phase 2 synthetic datasets reflect both normal banking activity and suspicious or fraudulent operational patterns.

### 🎯 Objectives
- generate realistic baseline banking behavior
- inject fraud scenarios with controlled distributions
- model downstream fraud-ops lifecycle outcomes
- support both broad synthetic coverage and curated demo scenarios

### 🧩 Scope
- account takeover behavior
- mule-transfer behavior
- card-not-present behavior
- false-positive review behavior
- alert, case, investigation, decision, and disposition lifecycle generation
- scenario summaries and lifecycle summaries in output metadata

### ✅ Acceptance Criteria
- generated batches include realistic fraud scenarios
- fraud events influence downstream alerts and case workflows
- lifecycle outputs are consistent with generated scenarios
- blueprint-driven runs can shape scenario counts and mixes

### 📦 Expected Outcome
A realistic fraud simulation layer that makes the synthetic data useful for fraud analytics, case-management design, and demo storytelling.

### 🔗 References
- `synthetic_generator/behavior.py`
- `synthetic_generator/fraud.py`
- `synthetic_generator/state.py`
- `documents/phase-2-dataset-design.md`
```

### #35 Export & Structure Data Files

```md
## 🔵 Phase 2 — Export & Structure Data Files

### 📌 Description
Export all Phase 2 generated outputs into a batch-oriented file structure that supports validation, traceability, and later ingestion into storage and warehouse layers.

### 🎯 Objectives
- write generated datasets as CSV files
- produce a clear landing, control, and quality folder structure
- emit manifest and control artifacts
- make outputs easy to inspect, validate, and ingest

### 🧩 Scope
- landing CSV export
- batch control artifact generation
- manifest generation
- validation output location
- stable output directory conventions

### ✅ Acceptance Criteria
- datasets are exported under `data/batches/<batch_id>/landing/csv/`
- `control/manifest.json` is written for each run
- `control/batch_control.json` is written for each run
- `quality/validation_report.json` is written when validation is enabled
- dataset row counts and run metadata are captured in control artifacts

### 📦 Expected Outcome
A governed file layout for synthetic batches that cleanly separates raw dataset exports from control and quality metadata.

### 🔗 References
- `synthetic_generator/exporter.py`
- `synthetic_generator/generate.py`
- `synthetic_generator/README.md`
```

### #36 Load Data into Object Storage (MinIO)

```md
## 🔵 Phase 2 — Load Data into Object Storage (MinIO)

### 📌 Description
Add optional MinIO upload support so generated Phase 2 batch artifacts can be published into the local object-storage sandbox for downstream ingestion and platform integration.

### 🎯 Objectives
- support object-storage handoff for generated artifacts
- keep local generation usable even when MinIO upload is not needed
- align object paths to the FraudLens raw-zone convention

### 🧩 Scope
- CLI flag for MinIO upload
- upload of generated batch artifacts
- path convention for Phase 2 outputs
- integration with local platform configuration

### ✅ Acceptance Criteria
- MinIO upload is optional
- generated artifacts can be uploaded after a successful run
- uploaded objects follow the expected FraudLens Phase 2 path structure
- upload behavior is documented for local use

### 📦 Expected Outcome
An optional object-storage publishing step that makes Phase 2 outputs easy to hand off into later ingestion and pipeline phases.

### 🔗 References
- `synthetic_generator/storage.py`
- `synthetic_generator/generate.py`
- `documents/platform-foundation-guide.md`
```

### #37 Validate Data Integrity & Relationships

```md
## 🔵 Phase 2 — Validate Data Integrity & Relationships

### 📌 Description
Validate generated Phase 2 batches for integrity, consistency, and relationship quality so synthetic outputs are trustworthy enough for downstream modeling and analytics work.

### 🎯 Objectives
- validate generated datasets after export
- check temporal consistency and behavioral consistency
- verify organization-structure consistency
- validate blueprint compliance when blueprint mode is used
- surface validation results in a machine-readable report

### 🧩 Scope
- integrity checks
- temporal consistency checks
- behavioral consistency checks
- organization consistency checks
- blueprint compliance checks
- validation status reporting

### ✅ Acceptance Criteria
- validation can be triggered through the generator CLI
- `validation_report.json` is produced when validation is enabled
- manifest output reflects validation status
- validation errors are captured clearly
- blueprint-mode batches include blueprint compliance results

### 📦 Expected Outcome
A validation layer that confirms generated Phase 2 batches are structurally sound, behaviorally plausible, and aligned to configured expectations.

### 🔗 References
- `synthetic_generator/validation.py`
- `synthetic_generator/generate.py`
- `tests/test_phase2_generator.py`
```
