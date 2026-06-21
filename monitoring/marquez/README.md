# Marquez Lineage Visualization

Issue: #80 — Integrate Lineage Visualization (Marquez)

## Purpose

This directory contains FraudLens Marquez configuration and helper assets for validating OpenLineage delivery and lineage visualization.

## Files

- `marquez.env.example`
  - local environment defaults for Marquez and OpenLineage endpoints
- `lineage-visualization-checklist.md`
  - operator checklist for confirming lineage in the Marquez UI

## Expected Local URLs

- Marquez API/UI: `http://localhost:3003`
- OpenLineage endpoint: `http://localhost:5000`

## Workflow

1. Generate local OpenLineage-compatible JSONL events.
2. Run delivery helper in dry-run mode.
3. Confirm Marquez health endpoint is reachable.
4. Deliver events to `OPENLINEAGE_URL`.
5. Open Marquez and validate the job, run, and dataset graph.
