# FraudLens Phase 2 Dataset Design

## Purpose

Phase 2 turns the existing governed contracts into generated physical datasets that can support ingestion, warehouse design, fraud analytics, and downstream pipeline development.

## Why 21 Datasets

Earlier issue wording referenced 10 datasets. The current governed model in `specs/` has expanded in two steps:

- 14 core banking and fraud-operations datasets
- 7 additional calendar, geography, and organization datasets for dashboard control and realistic operational ownership

Phase 2 intentionally implements the current governed model rather than collapsing it back to the older issue text.

## Generated Dataset Set

### Core And Master Data

- `party`
- `deposit_account`
- `payment_card`
- `device_profile`
- `channel_event`
- `reference_data_catalog`

### Calendar, Geography, And Organization Data

- `calendar_day`
- `region`
- `branch_territory`
- `branch_location`
- `business_unit`
- `analyst_team`
- `party_org_assignment`

### Transactional Data

- `payment_instruction`
- `payment_transaction`

### Fraud Operations Data

- `risk_signal`
- `fraud_alert`
- `fraud_case`
- `investigation_event`
- `decision_record`
- `case_disposition`

## Modeling Position

- the YAML contracts in `specs/` remain the design source of truth
- the Phase 2 generator aligns to those contracts, but is not fully code-generated from them
- the generated dataset is relational and ready for later Bronze/Silver/Gold and star-schema work

## Behavioral Simulation

Phase 2 includes:

- realistic baseline banking behavior
- rich fraud operations simulation
- deterministic generation using a seed
- seeded `Faker` support for more natural-looking reference text and session identifiers
- dual generation modes: mixed and blueprint-driven curated batches
- dashboard-control dimensions for region, branch territory, business unit, analyst team, and calendar periods
- batch-style export into landing, control, and quality areas
- validation reporting
- optional MinIO upload to `fraudlens-raw/phase2/<run_id>/`

## CLI Shape

Mixed mode:

```powershell
py -m synthetic_generator.generate --mode mixed --output-dir data --days 90 --profile medium_demo --seed 42 --validate
```

Curated built-in blueprint:

```powershell
py -m synthetic_generator.generate --mode blueprint --blueprint hybrid_fraud_ops_demo --output-dir data --profile medium_demo --seed 42 --validate
```

Curated custom blueprint file:

```powershell
py -m synthetic_generator.generate --mode blueprint --blueprint synthetic_generator/blueprints/custom/my_showcase.yaml --output-dir data --seed 42 --validate
```

List built-in blueprints:

```powershell
py -m synthetic_generator.generate --list-blueprints
```

## Scale Profiles

### `medium_demo`

- 90-day horizon
- suitable for showcase and downstream modeling demos
- realistic but still local-friendly row volumes

### `small_fast`

- reduced row counts
- intended for smoke tests and local iteration

## Output Artifacts

Every run produces:

- landing CSV files for all 21 datasets
- a batch control file with stage-by-stage execution metadata
- a manifest with run metadata, row counts, scenario summaries, and org/geography summaries
- a validation report with integrity, behavioral, and blueprint-compliance checks when applicable

## Blueprint Mode

Blueprint mode is a curated fraud-ops showcase flow. It keeps actor and event creation synthetic, but fixes macro targets through YAML:

- scenario counts
- lifecycle counts
- decision mix
- disposition mix
- timing style
- realism emphasis flags
- calendar controls
- geography mix
- organization mix
- customer mix
- payment rail and cross-border controls
- fraud-ops control mixes for alert source, case priority, decision reason, and recovery status

Built-in blueprints currently cover:

- `account_takeover_showcase`
- `mule_ring_showcase`
- `card_not_present_showcase`
- `false_positive_review_showcase`
- `hybrid_fraud_ops_demo`

## Dashboard Control Outcomes

The expanded contracts and generator now support more realistic management reporting, including:

- alerts by region and business unit
- case workload by analyst team
- branch-territory activity and fraud concentration
- monthly and quarterly trend views driven by the `calendar_day` dimension
- recovery, write-off, and fraud resolution reporting by ownership structure
