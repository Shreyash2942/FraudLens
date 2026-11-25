# Workflow layout and CI/CD strategy

The Phase 8 branch uses `ci.yml` for repository standards, offline dbt and Python validation, and `CI Summary`. Issue #86 migrates the previous path-filtered dbt checks; #87 adds generator/helper regression, correctness lint and repository standards. The [CI/CD strategy and release model](../../documents/cicd-strategy-release-model.md) defines the target operating model; [cicd-release-contract.yaml](../cicd-release-contract.yaml) distinguishes implemented checks from remaining policy work.

Issues #84–#88 define the strategy, validation and deployment implementation. #89 configures no-spend environment controls and local Docker handoffs. The workflows become the `main` baseline after the Phase 8 PR merges; actual runtime qualification and final handoff remain #90/#91. Required `CI Summary` enforcement is sealed only after successful CI on actual merged `main`.

## Current and planned workflow responsibilities

- `ci.yml` — implemented in #85–#87
  - triggers for every PR targeting `main`, including drafts and docs-only changes, without workflow-level path filters
  - also validates `push` to `main`; manual dispatch is available after the workflow exists on the default branch
  - ephemeral Ubuntu 24.04 runner, Python 3.11, read-only repository token, commit-pinned actions, and no deployment environment or secrets
  - validates required tracked files, tracked Python syntax, YAML parsing, and private/generated-file hygiene
  - runs 52 CI regression tests; validates governed metadata, tracked Markdown destinations and local-only cost/workflow boundaries
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
  - #89 replaces the initial self-hosted-runner path with an approved hosted handoff and an explicit owner-operated local Docker adapter; no public workflow runs on the developer's container
  - private service settings remain in an owner-only file on the existing Docker volume; GitHub requires no runtime secrets
  - local activation retains the managed source/import/maintenance/pointer checks; it neither starts a pipeline nor rolls back data
  - activation waits for merged main CI, owner environment approval and the explicit local operator command; #90 supplies real runtime qualification
  - see [issue #88 workflow and activation guide](../../documents/phase-8-plan/issue-88-deployment-workflow.md)

## Workflow Design Rules

- PR validation must be fast and deterministic.
- Governance checks must fail loudly on missing required metadata.
- Release workflows must target `main` only.
- Pull-request validation uses ephemeral hosted runners with read-only repository access and no deployment secrets.
- Candidate validation must repeat on the resulting `main` SHA before runtime promotion.
- Deployment and secret controls are implemented under #88 and #89 after the validation gates are available.
- Every runner job has a public-repository guard and uses standard Ubuntu 24.04. The portfolio provisions no cloud accounts, paid runners or test/prod compute.
- `CI Summary` aggregates baseline/standards, offline dbt, Python and candidate packaging. See [#89 controls and local operation](../../documents/phase-8-plan/issue-89-environment-controls.md) for applied settings and the post-merge status-check seal.
