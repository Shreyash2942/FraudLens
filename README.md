# FraudLens

FraudLens is a standards-first banking fraud analytics project built around a realistic operating model for payments, accounts, fraud risk, and case management.

Phase 0 establishes the repository foundation only. This repo intentionally focuses on design contracts, governance, and GitHub workflow conventions before executable implementation begins.

## Phase 0 Scope

- Canonical project documentation
- Versioned schema and dataset contracts under `specs/`
- SOX-aligned governance and auditability standards
- GitHub-ready templates, workflow conventions, and contribution guidance
- Placeholder technical areas for later phases

Docker, local containers, orchestration code, dbt models, SQL DDL, and generators are out of scope for this phase.

## Design Principles

- ISO 20022-inspired semantic structure for payments, accounts, and transactions
- BIAN-inspired domain grouping and business naming
- Purpose-built fraud operations resources for alerts, cases, investigations, and decisions
- Strong traceability, ownership, and control design aligned to SOX-style expectations

## Repository Layout

- `.github/` GitHub templates, workflow conventions, and code ownership
- `documents/` charter, roadmap, architecture, governance, and project management docs
- `specs/` versioned structured contracts and relationship definitions
- `standards/` naming, modeling, controls, and auditability standards
- `airflow/`, `dbt/`, `warehouse/`, `monitoring/`, `analytics/`, `data/`, `platform/` reserved technical roots for later phases

## Getting Started

Start with these documents:

1. `documents/project-charter.md`
2. `documents/implementation-roadmap.md`
3. `documents/architecture-overview.md`
4. `specs/README.md`
5. `standards/README.md`

## Current Status

Phase 0 is implemented as a repo baseline. Phase 1 and later phases will add executable assets on top of the standards defined here.
