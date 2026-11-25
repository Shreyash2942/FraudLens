# CI/CD workflows and release process

Operational handoff for [issue #91](https://github.com/Shreyash2942/FraudLens/issues/91), Phase 8. Reviewed November 24, 2026 (America/New_York).

This is the current operator guide. [The strategy](cicd-strategy-release-model.md) explains design decisions; [the release contract](../.github/cicd-release-contract.yaml) records policy; dated [issue guides](phase-8-plan/README.md) preserve implementation evidence. Older pre-merge prerequisites and the original self-hosted runner design are superseded by this guide and current workflow/source.

## Current delivery position

[PR #122](https://github.com/Shreyash2942/FraudLens/pull/122) merged into main at `908011163499d5d1e75f2076dc5a57651dfd3c92`. [Main-push CI run 45545800298](https://github.com/Shreyash2942/FraudLens/actions/runs/45545800298) passed. Main now requires up-to-date successful `CI Summary` from GitHub Actions (app ID `15368`), PR integration and resolved conversations. Protections include administrators and forbid force pushes/deletion. The sole maintainer records owner acceptance; required approving-review count is zero, without claiming independent review.

The owner closed #83/#90 during the Phase 9 transition. Issue closure does not certify a real protected handoff, local source activation, full data-pipeline run or runtime failure/recovery: those outcomes have not been demonstrated by the recorded Phase 8 qualification. This guide documents the implemented path and remaining operational proof.

## CI purpose and triggers

[`ci.yml`](../.github/workflows/ci.yml), named **Code Validation**, validates source and packages an immutable candidate after successful validation.

| Event | Scope and behavior |
| --- | --- |
| Main-targeting `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review`, `edited`; includes drafts and docs-only changes, with no workflow path filter. Preview bundles only. |
| `push` to `main` | Revalidates the exact merged main SHA; the only CI origin accepted for promotion. |
| `workflow_dispatch` | Manual validation on a selected ref. Even manual CI on main produces a preview: promotion requires a successful **push** run. |

Every runner job requires a public repository and standard `ubuntu-24.04`. Validation uses Python 3.11, read-only tokens, pinned action commits and no deployment environment/runtime service secrets. A newer run for the same PR cancels older PR CI. A branch push outside main needs a main-targeting PR to trigger CI.

| Gate | Required validation |
| --- | --- |
| Baseline Repository Checks | Tracked-file syntax/YAML/hygiene, CI regression, 21 governed contracts, tracked Markdown destinations and local-only portfolio/workflow policy. |
| dbt Validation | Pinned dbt/Hive dependencies, full offline parse, actual failure-selector coverage, naming/governance/contract/policy validators and empty-catalog docs. No warehouse SQL compile/build/data tests. |
| Python Validation | Tracked Ruff correctness checks; generator/helper and Airflow tests in a temporary clean tracked-source snapshot. External service outcomes in isolated tests use fixtures. |
| Deployment Validation / Candidate Bundle | Reusable `deploy.yml` with typed `ci_bundle=true`, after baseline/dbt/Python success. Packages regular committed source blobs and digests, without deployment environment association. |
| CI Summary | All four preceding gate results must be `success`; failure, cancellation, missing or skipped required results fail. All 1,296 result combinations have regression coverage. |

Baseline/dbt/Python/package jobs have ten-minute timeouts; the aggregate has two minutes. Dispatch-only verify/handoff jobs are intentionally skipped during CI; this is separate from skipping a required gate. Only `ci.yml` and `deploy.yml` exist: governance is integrated into CI, and release publication has no automated workflow.

## Run and inspect validation

Use Python 3.11 in a virtual environment from the repository root. Stage new files before validation so the tracked-source inventory includes them:

```text
python -m pip install -r requirements-python-ci.txt
python -m unittest discover -s tests/ci -p test_*.py -v
python scripts/ci/validate_repository.py --report .ci-artifacts/repository-checks.json
python -m scripts.ci.validate_standards
python -m scripts.deployment.environment_audit
python -m scripts.ci.validate_python --stage lint
python -m scripts.ci.validate_python --stage tests
```

For offline dbt reproduction, follow [the dbt CI guide](phase-8-plan/issue-86-dbt-validation.md): the Hive adapter needs Linux system libraries as well as `requirements-dbt-ci.txt`. Hosted CI provides the exact Ubuntu/Python environment. The full Airflow CI profile is not offline validation.

```text
gh pr checks <pr-number> --repo Shreyash2942/FraudLens
gh run view <run-id> --repo Shreyash2942/FraudLens
gh run view <run-id> --repo Shreyash2942/FraudLens --log-failed
gh run download <run-id> --repo Shreyash2942/FraudLens --dir .ci-artifacts/review/<run-id>
```

Replace angle-bracket placeholders before running command templates. Review head SHA **and** tested merge SHA, event, workflow, run ID/attempt, gate results and report provenance. `python-validation.json` records dependencies/JUnit totals; baseline/standards/dbt/policy reports are sanitized. Reports and candidate artifacts have 30-day retention. Preserve needed evidence before expiry; expired artifacts require a newly validated candidate.

The artifact `candidate-<sha>-<ci-run-id>-<attempt>` contains `candidate.tar`, `candidate.sha256`, `candidate-report.json`. Its tar contains `manifest.json` and `payload/` committed source. Verify the API ZIP digest, selected tar SHA-256 and every manifest file hash. A green PR or downloaded preview never authorizes promotion.
