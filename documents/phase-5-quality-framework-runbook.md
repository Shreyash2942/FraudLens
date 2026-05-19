# Phase 5 Quality Framework Runbook

## Purpose

This runbook explains how to execute the Phase 5 quality framework in local and CI-style modes using dbt selectors and severity gates.

## Prerequisites

- dbt project available at `dbt/`
- profile: `fraudlens_local_spark`
- selectors file: `dbt/selectors.yml`

## Core Modes

### 1. Parse And Inventory

Use before every validation run:

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### 2. Strict Critical Gate

Hard-stop path for unsafe quality states:

```bash
dbt test --selector quality_critical_gate --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### 3. High-Severity Gate

Readiness-risk validation:

```bash
dbt test --selector quality_high_gate --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### 4. Category Runs

```bash
dbt test --selector quality_not_null --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_unique --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_relationships --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_accepted_values --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

### 5. Layer Runs

```bash
dbt test --selector quality_bronze --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_silver --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --selector quality_gold --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

## Failure Handling Guidance

- critical gate failures (`quality_critical_gate`) block pipeline progression
- high gate failures block release/readiness signoff
- category/layer runs support triage and root-cause isolation

## Suggested Execution Sequence

1. `dbt parse`
2. `dbt ls`
3. `dbt test --selector quality_critical_gate`
4. `dbt test --selector quality_high_gate`
5. targeted category/layer selector runs as needed

## Reporting Notes

For readiness evidence, capture:
- executed selector names
- timestamp
- pass/fail summary
- blockers and owning follow-up issue
