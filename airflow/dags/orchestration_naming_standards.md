# Orchestration Naming And Operator Standards

## DAG Naming

- use `fraudlens_<workflow_name>` pattern for DAG IDs
- use snake_case for file names and task IDs
- use explicit gate task IDs: `<stage>_complete_gate`

## Operator Use

- `EmptyOperator` for control boundaries and no-op gates
- `BashOperator` for script-backed execution and artifact publishing
- `TaskGroup` for stage-level grouping and UI readability

## Runtime Inputs

- `profile`: orchestration profile (`local`, `ci`, `snowflake`)
- `batch_id`: explicit batch override or `latest`
- dataset override remains comma-separated and validated against governed dataset order
