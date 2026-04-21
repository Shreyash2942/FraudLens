# GitHub Project Management Baseline

## Milestones

Create the following milestones in GitHub:

- `Phase 0 - Project Initialization And Planning`
- `Phase 1 - Platform Foundation`
- `Phase 2 - Dataset And Data Design`
- `Phase 3 - Warehouse Setup`
- `Phase 4 - Transformation Layer`
- `Phase 5 - Data Quality And Governance`
- `Phase 6 - Orchestration`
- `Phase 7 - Observability And Lineage`
- `Phase 8 - CI/CD`
- `Phase 9 - Analytics And Dashboards`
- `Phase 10 - Finalization And Professionalization`

## Label Taxonomy

### Phase Labels

- `phase:0`
- `phase:1`
- `phase:2`
- `phase:3`
- `phase:4`
- `phase:5`
- `phase:6`
- `phase:7`
- `phase:8`
- `phase:9`
- `phase:10`

### Type Labels

- `type:epic`
- `type:task`
- `type:bug`
- `type:docs`

### Area Labels

- `area:platform`
- `area:data`
- `area:warehouse`
- `area:dbt`
- `area:airflow`
- `area:observability`
- `area:cicd`
- `area:bi`
- `area:governance`

### Priority Labels

- `priority:p0`
- `priority:p1`
- `priority:p2`
- `priority:p3`

### Status Labels

- `status:ready`
- `status:in-progress`
- `status:blocked`
- `status:review`

## Issue Model

- one phase epic issue per milestone
- linked design or implementation tasks under each phase
- governance changes tracked separately when they affect controls or approval models

## Note

The local environment currently does not have authenticated GitHub CLI access, so these milestones and labels are documented here and can be created once `gh auth login` or an equivalent token-based setup is available.
