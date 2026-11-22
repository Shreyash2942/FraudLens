# Workflow layout and CI/CD strategy

The Phase 8 branch uses `ci.yml` for repository standards, offline dbt and Python validation, and `CI Summary`. Issue #86 migrates the previous path-filtered dbt checks; #87 adds generator/helper regression, correctness lint and repository standards. The [CI/CD strategy and release model](../../documents/cicd-strategy-release-model.md) defines the target operating model; [cicd-release-contract.yaml](../cicd-release-contract.yaml) distinguishes implemented checks from remaining policy work.

Issues #84–#87 define the strategy and implement validation; #88 adds candidate packaging and controlled deployment on the feature branch. The workflows become the `main` baseline after the Phase 8 PR merges. Enforcement, activation prerequisites, runtime qualification and handoff remain #89–#91; policy documentation alone does not configure GitHub protection settings.

## Current and planned workflow responsibilities

- `ci.yml` — implemented in #85–#87
  - triggers for every PR targeting `main`, including drafts and docs-only changes, without workflow-level path filters
  - also validates `push` to `main`; manual dispatch is available after the workflow exists on the default branch
  - ephemeral Ubuntu 24.04 runner, Python 3.11, read-only repository token, commit-pinned actions, and no deployment environment or secrets
  - validates required tracked files, tracked Python syntax, YAML parsing, and private/generated-file hygiene
  - runs 40 CI regression tests; validates governed entity naming/ownership/audit metadata and tracked Markdown destinations
  - `Python Validation` uses pinned dependencies, lints all tracked Python files with Ruff correctness rules, and runs the full generator/helper suite in a clean tracked-source snapshot
  - uploads only sanitized baseline, standards, dbt and Python JSON reports for 30 days
  - installs pinned dbt-core/Hive dependencies and performs a full offline parse using a dedicated credential-free CI profile
  - requires both failure-policy test selectors to select actual tests; runs all five established naming/governance/contract/policy validators and empty-catalog docs generation without SQL compilation
  - invokes `deploy.yml` for secret-free candidate packaging after baseline/dbt/Python success; PR bundles are explicitly preview-only
  - `CI Summary` also requires deployment packaging; tests cover all 1,296 result combinations across four gates
  - see [issue #85 execution and reproduction guide](../../documents/phase-8-plan/issue-85-code-validation.md)
  - see [issue #86 validation and failure evidence](../../documents/phase-8-plan/issue-86-dbt-validation.md)
  - see [issue #87 Python and repository standards evidence](../../documents/phase-8-plan/issue-87-python-standards.md)
- `governance-checks.yml`
  - verify required ownership and control metadata
  - detect missing audit fields in governed contracts
  - enforce naming standards for new datasets
- `main-release.yml`
  - reserved for later release publication; candidate packaging and controlled dev deployment are in `deploy.yml`
- `deploy.yml` — implemented in #88
  - reusable CI path builds and verifies source bundles with per-file and archive digests; it has no environment association
  - manual `verify`/`deploy` requires owner dispatch from `main`, successful push-to-main CI for the exact candidate, matching artifact/digests, explicit acceptance and existing environment protections
  - only `dev`/`local` is implemented; `test` and `prod` fail preflight
  - protected activation uses a dedicated trusted Linux runner, a managed release store, Airflow import/maintenance checks and an atomic code pointer; it neither starts a pipeline nor rolls back data
  - activation is blocked until #89 configures controls and infrastructure, and the workflow merges to `main`; #90 supplies actual runtime qualification
  - see [issue #88 workflow and activation guide](../../documents/phase-8-plan/issue-88-deployment-workflow.md)

## Workflow Design Rules

- PR validation must be fast and deterministic.
- Governance checks must fail loudly on missing required metadata.
- Release workflows must target `main` only.
- Pull-request validation uses ephemeral hosted runners with read-only repository access and no deployment secrets.
- Candidate validation must repeat on the resulting `main` SHA before runtime promotion.
- Deployment and secret controls are implemented under #88 and #89 after the validation gates are available.
- `CI Summary` aggregates baseline/standards, offline dbt, Python and candidate packaging. Warehouse-backed data tests remain runtime qualification; #89 branch protection and live deployment controls remain pending.
