# Reserved Workflow Layout

Phase 0 does not add executable GitHub Actions workflows. This directory defines the intended structure for later phases.

## Planned Workflow Names

- `pr-validation.yml`
  - validate Markdown and YAML structure
  - enforce required spec metadata
  - run Python quality checks when Python assets exist
  - run dbt structure validation when dbt assets exist
- `governance-checks.yml`
  - verify required ownership and control metadata
  - detect missing audit fields in governed contracts
  - enforce naming standards for new datasets
- `main-release.yml`
  - reserved for release, packaging, deployment, or promoted artifact workflows in later phases

## Workflow Design Rules

- PR validation must be fast and deterministic.
- Governance checks must fail loudly on missing required metadata.
- Release workflows must target `main` only.
- Secrets and deployment logic must remain out of Phase 0.
