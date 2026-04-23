# Specs

`specs/` contains the primary design contracts for FraudLens.

## Structure

- one folder per business domain
- one or more versioned contracts per domain
- shared semantics and cross-domain relationships at the top level

## Key Files

- `semantic-conventions.yaml`
- `relationship-map.yaml`

## Domain Groups

- `payments/`
- `accounts/`
- `calendar/`
- `geography/`
- `organization/`
- `parties/`
- `channels/`
- `cards/`
- `devices/`
- `reference/`
- `risk/`
- `alerts/`
- `cases/`
- `investigations/`
- `decisions/`
- `dispositions/`

These contracts are design assets, not executable schemas. Later phases may translate them into physical models, warehouse DDL, dbt sources, and marts.
