# Workflow layout and CI/CD strategy

The Phase 8 branch adds `ci.yml` for always-reporting baseline code validation and `CI Summary`. `pr-validation.yml` retains the existing, separate path-filtered dbt checks. The [CI/CD strategy and release model](../../documents/cicd-strategy-release-model.md) defines the target operating model; [cicd-release-contract.yaml](../cicd-release-contract.yaml) distinguishes implemented checks from remaining policy work.

Issue #84 defines the strategy. Issue #85 delivers the CI foundation on the feature branch. The workflow becomes the `main` baseline after the Phase 8 PR merges. Full dbt/Python/standards integration and enforcement remain #86–#91; policy documentation alone does not configure GitHub protection settings.

## Current and planned workflow responsibilities

- `ci.yml` — implemented in #85
  - triggers for every PR targeting `main`, including drafts and docs-only changes, without workflow-level path filters
  - also validates `push` to `main`; manual dispatch is available after the workflow exists on the default branch
  - ephemeral Ubuntu 24.04 runner, Python 3.11, read-only repository token, commit-pinned actions, and no deployment environment or secrets
  - validates required tracked files, tracked Python syntax, YAML parsing, and private/generated-file hygiene
  - runs 11 CI-foundation regression tests and uploads only the sanitized report for 30 days
  - `CI Summary` runs after baseline failure and succeeds only when the baseline result is exactly `success`
  - see [issue #85 execution and reproduction guide](../../documents/phase-8-plan/issue-85-code-validation.md)
- `pr-validation.yml`
  - current: path-filtered dbt structure validation and empty-catalog docs generation
  - #86 integrates dbt validation into the new aggregate gate without weakening the existing validators
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
- `CI Summary` currently aggregates the #85 baseline only. Do not interpret it as proof that #86/#87 checks or #89 branch protection have been implemented.
