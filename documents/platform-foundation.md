# Platform Foundation (Phase 1)

Status date: `2026-05-25`
Milestone scope: `#21` with sub-issues `#22`-`#28`

## Purpose

This document consolidates Phase 1 platform integration expectations and validation steps for FraudLens.

## Primary Phase File

Use this as the primary Phase 1 review and handoff file in `documents/`.

## Scope Consolidated

- `#22` Setup Docker environment
- `#23` Configure Airflow and metadata database
- `#24` Setup object storage (MinIO)
- `#25` Implement monitoring (Prometheus + Grafana)
- `#26` Setup lineage tracking (Marquez + OpenLineage)
- `#27` Validate platform and service connectivity
- `#28` Document platform setup

## Executive Outcome

Phase 1 established the external runtime contract and local validation baseline:

- FraudLens uses `Shreyash2942/Data-Lab` as the canonical local runtime source
- this repository documents platform expectations instead of duplicating Docker stack ownership
- local all-in-one container usage is accepted for cost-efficient development
- Snowflake remains the target analytics direction while Spark/Hive can support local surrogate workflows
- service interfaces, dependency order, and validation evidence expectations are defined

## Runtime Contract

FraudLens depends on these logical capabilities:

- Airflow for orchestration
- PostgreSQL for metadata persistence
- MinIO for object landing and exchange
- Prometheus for metrics scraping
- Grafana for operational dashboards
- Marquez/OpenLineage for lineage capture

Default endpoint expectations are documented in source guides and can be overridden via local `.env` when runtime port mappings differ.

## Validation Baseline

Validation follows a fixed order:

1. Docker runtime availability
2. Airflow reachability
3. PostgreSQL metadata availability
4. MinIO accessibility
5. Prometheus availability
6. Grafana availability
7. Marquez/OpenLineage availability
8. runtime log sanity (no recurring critical failures)

Minimum Definition of Done evidence requires all critical interfaces reachable and no blocking runtime faults.

## Workstream Mapping

- setup and integration rules are documented without runtime duplication in this repo
- service contracts and environment assumptions are explicitly captured
- connectivity checks and failure follow-up are standardized for issue tracking

## Consolidation Source Set

- `documents/platform-foundation-guide.md`
- `documents/platform-validation-runbook.md`

## Reviewer Notes

Use this as the retained Phase 1 review artifact.
