# Workflow layout and CI/CD strategy

Use the [CI/CD workflows and release process](../../documents/cicd-workflows-release-process.md) for current commands, controls, release guidance and troubleshooting. `ci.yml` implements repository standards, offline dbt, Python and required `CI Summary`; `deploy.yml` packages candidates and prepares protected local Docker handoffs. The [strategy](../../documents/cicd-strategy-release-model.md) records design rationale and [release contract](../cicd-release-contract.yaml) records policy.

These workflows are merged into main through PR #122. Required `CI Summary` enforcement was enabled after successful actual-main run 45545800298. Issue #89 configured no-spend logical environments and private local secrets. Runtime activation/pipeline qualification is not established by issue closure or this documentation.

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
- `deploy.yml` — implemented in #88
  - reusable CI path builds and verifies source bundles with per-file and archive digests; it has no environment association
  - manual `verify`/`deploy` requires owner dispatch from `main`, successful push-to-main CI for the exact candidate, matching artifact/digests, explicit acceptance and existing environment protections
  - only `dev`/`local` is implemented; `test` and `prod` fail preflight
  - #89 replaces the initial self-hosted-runner path with an approved hosted handoff and an explicit owner-operated local Docker adapter; no public workflow runs on the developer's container
  - private service settings remain in an owner-only file on the existing Docker volume; GitHub requires no runtime secrets
  - local activation retains the managed source/import/maintenance/pointer checks; it neither starts a pipeline nor rolls back data
  - main CI is verified; activation still requires owner environment approval and the explicit local operator command; real runtime/pipeline qualification is not yet certified
  - see [issue #88 workflow and activation guide](../../documents/phase-8-plan/issue-88-deployment-workflow.md)

## Workflow Design Rules

- PR validation must be fast and deterministic.
- Governance checks must fail loudly on missing required metadata.
- Release workflows must target `main` only.
- Pull-request validation uses ephemeral hosted runners with read-only repository access and no deployment secrets.
- Candidate validation must repeat on the resulting `main` SHA before runtime promotion.
- Deployment and secret controls are implemented under #88 and #89 after the validation gates are available.
- Every runner job has a public-repository guard and uses standard Ubuntu 24.04. The portfolio provisions no cloud accounts, paid runners or test/prod compute.
- `CI Summary` aggregates baseline/standards, offline dbt, Python and candidate packaging. Main enforces that exact check with strict/up-to-date integration. Only `ci.yml` and `deploy.yml` exist; governance is integrated into CI and automated release publication is not implemented.
