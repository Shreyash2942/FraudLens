# Workflow layout and CI/CD strategy

The Phase 8 branch uses `ci.yml` for baseline repository checks, offline dbt validation, and `CI Summary`. Issue #86 migrates the previous path-filtered `pr-validation.yml` checks into this workflow. The [CI/CD strategy and release model](../../documents/cicd-strategy-release-model.md) defines the target operating model; [cicd-release-contract.yaml](../cicd-release-contract.yaml) distinguishes implemented checks from remaining policy work.

Issue #84 defines the strategy, #85 delivers the foundation, and #86 integrates dbt validation on the feature branch. The workflow becomes the `main` baseline after the Phase 8 PR merges. Broader Python/standards integration and enforcement remain #87–#91; policy documentation alone does not configure GitHub protection settings.

## Current and planned workflow responsibilities

- `ci.yml` — implemented in #85 and #86
  - triggers for every PR targeting `main`, including drafts and docs-only changes, without workflow-level path filters
  - also validates `push` to `main`; manual dispatch is available after the workflow exists on the default branch
  - ephemeral Ubuntu 24.04 runner, Python 3.11, read-only repository token, commit-pinned actions, and no deployment environment or secrets
  - validates required tracked files, tracked Python syntax, YAML parsing, and private/generated-file hygiene
  - runs 17 CI regression tests and uploads sanitized baseline/dbt reports for 30 days
  - installs pinned dbt-core/Hive dependencies and performs a full offline parse using a dedicated credential-free CI profile
  - requires both failure-policy test selectors to select actual tests; runs all five established naming/governance/contract/policy validators and empty-catalog docs generation without SQL compilation
  - `CI Summary` runs after either job fails and succeeds only when both results are exactly `success`
  - see [issue #85 execution and reproduction guide](../../documents/phase-8-plan/issue-85-code-validation.md)
  - see [issue #86 validation and failure evidence](../../documents/phase-8-plan/issue-86-dbt-validation.md)
- #87 extends the baseline with the broader Python suite and repository/domain standards, including documentation links and governance metadata
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
- `CI Summary` aggregates the #85 baseline and #86 offline dbt checks. Warehouse-backed data tests remain runtime qualification; broader #87 checks and #89 branch protection remain pending.
