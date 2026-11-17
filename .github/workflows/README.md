# Workflow layout and CI/CD strategy

`pr-validation.yml` currently implements path-filtered dbt structure and documentation checks. The Phase 8 [CI/CD strategy and release model](../../documents/cicd-strategy-release-model.md) defines the target operating model; [cicd-release-contract.yaml](../cicd-release-contract.yaml) records its policy and the observed baseline.

Issue #84 defines the strategy. Workflow implementation and enforcement belong to issues #85–#91. Policy documentation alone does not enforce a merge or deployment gate.

## Current and planned workflow responsibilities

- `pr-validation.yml`
  - current: path-filtered dbt structure validation and empty-catalog docs generation
  - planned: an always-reporting `CI Summary` gate with repository, Python, and dbt validation
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
- Pull-request validation uses ephemeral hosted runners with read-only repository access and no deployment secrets.
- Candidate validation must repeat on the resulting `main` SHA before runtime promotion.
- Deployment and secret controls are implemented under #88 and #89 after the validation gates are available.
