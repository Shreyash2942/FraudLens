# Issue #80 Plan - Integrate Lineage Visualization With Marquez

Issue: `#80`

Phase: `Phase 7 - Observability And Lineage`

Status date: `2026-06-17`

## Description Alignment

Configure and validate Marquez as the local lineage visualization layer for OpenLineage events emitted by FraudLens workflows.

## Task Breakdown

### 1. Confirm runtime integration

- document Data-Lab Marquez endpoint and health check expectations
- define environment variables for local and CI-safe configuration
- verify namespace naming aligns with OpenLineage mapping

### 2. Connect OpenLineage delivery

- configure event destination to Marquez ingestion API
- validate API availability before event submission
- log delivery status and failure reason safely

### 3. Validate lineage UI

- run or document a representative pipeline lineage submission
- confirm Marquez shows jobs, runs, inputs, and outputs
- capture validation evidence path and checklist

### 4. Document operations

- document health checks, endpoint configuration, and common failure modes
- document how to reset or re-run lineage submissions locally if supported
- link Marquez troubleshooting back to logging and metric signals

## Deliverables

- Marquez configuration notes under `monitoring/` or `documents/`
- environment variable contract for lineage endpoint setup
- lineage visualization validation checklist
- runbook updates

## Acceptance Criteria Mapping

- Marquez displays lineage correctly
- OpenLineage events reach the configured Marquez endpoint
- job/run/dataset names are understandable and governed
- local troubleshooting steps are documented

## Risk Notes

- Marquez may be available in Data-Lab but not in CI; keep CI checks contract-based
- incorrect namespaces can fragment lineage into multiple disconnected views
- replaying old events needs clear run identifiers to avoid confusing validation evidence

## Open Decision Log

- confirm Marquez API base URL used by Data-Lab
- confirm whether UI screenshot evidence is required for issue closeout
- confirm event replay strategy for local development
