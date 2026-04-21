# FraudLens Architecture Overview

## Architectural Intent

FraudLens separates business-domain design from technical implementation so that later warehouse and analytics work inherits stable entity boundaries, naming, and controls.

## Environment Strategy

- target analytical platform: Snowflake
- local development and cost-control platform: Data-Lab
- local warehouse surrogate for experimentation and selected testing: Spark and Hive

This project is intentionally designed as a professional portfolio artifact rather than a full production deployment. The local runtime may package multiple logical capabilities inside one container if that is the most practical way to iterate without unnecessary Snowflake spend.

## Domain Groups

- `payments` payment instruction and transaction movement
- `accounts` deposit account state and balances
- `parties` customers, counterparties, and role assignments
- `channels` origin and touchpoint context
- `cards` payment instrument context
- `devices` device and session identity signals
- `reference` reusable code sets and enumerations
- `risk` scored or derived fraud indicators
- `alerts` operational alert generation
- `cases` case-management records
- `investigations` analyst activity and evidence tracking
- `decisions` adjudication and control outcomes
- `dispositions` final closure and reporting outcomes

## Intended Data Flow

1. source and synthetic events land in raw storage
2. ingestion loads governed contracts into analytical storage
3. transformations produce standardized business entities
4. fraud analytics and case-management outputs feed BI and operational reporting

## Structural Conventions

- `specs/` contains the logical contract definitions
- `standards/` defines naming, controls, and modeling requirements
- later technical layers must map back to these contracts instead of inventing new business meanings

## Technology Position

The current repository reserves conventional technical roots for future implementation:

- `airflow/`
- `dbt/`
- `warehouse/`
- `monitoring/`
- `analytics/`
- `data/`
- `platform/`

Those locations began as placeholders in Phase 0. In Phase 1, `platform/` documents how FraudLens connects to the external Data-Lab runtime while keeping Snowflake as the long-term analytical target.
