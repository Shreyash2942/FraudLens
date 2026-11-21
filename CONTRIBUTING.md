# Contributing To FraudLens

FraudLens uses a standards-first delivery model. Every material change should begin with a tracked issue and should preserve alignment between documentation, specs, and governance controls.

## Working Rules

- Link every pull request to a GitHub issue.
- Update impacted specs and standards in the same change.
- Do not add runtime code, SQL, DAGs, or generators to Phase 0 scope unless explicitly requested.
- Prefer business-domain names in `specs/` and technical names in implementation folders.
- Treat YAML contracts under `specs/` as the primary design source of truth.

## Pull Request Expectations

- Explain what changed and why.
- List impacted domains and spec files.
- State whether controls, ownership, or auditability assumptions changed.
- Document manual validation performed.

## Branching Convention

- `main` is the integration branch.
- Feature branches should use `NN-short-slug`.
- Branch names should reflect the issue being addressed.

## CI/CD And Merge Policy

The [CI/CD strategy and release model](documents/cicd-strategy-release-model.md) and [operational contract](.github/cicd-release-contract.yaml) define the Phase 8 delivery policy.

- Use an issue-linked PR into `main`, preserve task-level commits, and include validation and control-impact evidence.
- Require passing checks for the current revision and resolve review conversations before merging.
- Record independent review when another qualified maintainer is available. A sole maintainer records explicit owner acceptance and the review checklist; do not describe this as independent approval.
- Use the phase merge commit to preserve the issue and task history. Promote a validated `main` commit rather than an environment branch.
- Treat branch protection, aggregate checks, and environment controls as planned until their implementation issues provide enforcement evidence.

## Automated Python And Repository Checks

Use Python 3.11 to match the hosted CI runner. From the repository root, install `requirements-python-ci.txt`, then run:

```bash
python -m pip install -r requirements-python-ci.txt
python -m scripts.ci.validate_python --stage lint
python -m scripts.ci.validate_python --stage tests
python -m scripts.ci.validate_standards
```

The test runner copies current Git-tracked source into a temporary workspace. Stage newly added files with `git add` before validating them; ignored local `.env`, runtime configuration, generated data, and inherited MinIO settings are excluded. Tests use temporary generated data and mocked service clients. They do not require a warehouse, Airflow installation, or external services.

Ruff checks correctness using `ruff.toml`; CI does not rewrite source. Repository checks enforce tracked-file hygiene, governed contract naming/ownership/audit metadata, and local Markdown destinations. See the [automated standards policy](standards/README.md) and [issue #87 guide](documents/phase-8-plan/issue-87-python-standards.md). `CI Summary` requires baseline/standards, dbt, and Python validation to succeed; GitHub enforcement is configured separately under #89.

## Definition Of Ready For Design Changes

- Business purpose is clear.
- Affected domains are identified.
- Control and audit impact is understood.
- Naming follows the repo standards.

## Definition Of Done For Phase 0 Artifacts

- Documentation is internally consistent.
- Structured specs validate conceptually against the modeling standard.
- Ownership and control metadata are present for critical entities.
- Active project content consistently uses the `FraudLens` name.
