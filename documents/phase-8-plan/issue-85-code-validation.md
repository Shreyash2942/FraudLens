# Issue #85: code validation workflow

Issue: [#85](https://github.com/Shreyash2942/FraudLens/issues/85)  
Parent: [#83](https://github.com/Shreyash2942/FraudLens/issues/83)  
Branch: `83-phase-8-cicd-implementation`  
Validation date: November 18, 2026 (America/New_York; API timestamps use November 19 UTC)

## Delivery and task commits

The [Code Validation workflow](../../.github/workflows/ci.yml) implements the foundation from [issue #84's strategy](../cicd-strategy-release-model.md). It validates incoming PRs without contacting Data-Lab, MongoDB, MinIO, or Snowflake. It is delivered through four task commits:

| Task | Delivery |
| --- | --- |
| 1. Create CI workflow file | `ci.yml`: bounded hosted jobs, read-only permissions, pinned checkout/setup actions, and a stable `CI Summary`. |
| 2. Trigger workflow on pull requests | All PR paths targeting `main`, including drafts; also `push` to `main` and manual dispatch. Cancel superseded PR checks, not in-progress `main` candidate validation. |
| 3. Add baseline repository checks | Tracked-file Python/YAML validation, repository foundations, private/generated-file hygiene, 11 regression tests, and a sanitized 30-day report artifact. |
| 4. Validate workflow execution | Passing phase PR and deliberately failing probe on GitHub Actions, downloaded report inspection, clean-source regression, documentation, and scoped graph refresh. |

## Checks and boundaries

`scripts/ci/validate_repository.py` uses `git ls-files` as its input inventory. It never imports or executes the inspected Python files. It parses Python with the configured CI interpreter and parses YAML safely. Ignored local configuration and generated data are not read. Tracked private `.env` files, generator runtime configuration, generated output, missing required files, unsafe symlinks, unreadable Python/YAML files, and syntax errors fail validation. Safe `.env.example`, `.env.sample`, and `.env.template` files are permitted.

Diagnostics identify the path, failure category, and line when available without copying source or configuration values. The artifact contains counts, error locations, tested checkout SHA, PR head/base SHAs, workflow run/attempt, and timestamp. Its upload path is the exact report file, not a broad directory of workspace contents. `include-hidden-files` permits that report's `.ci-artifacts/` parent; no other hidden files are uploaded.

The baseline job runs `tests/ci` before checking repository files. These 11 tests prove syntax rejection, private-file handling, ignored-config isolation, inventory failures, PR trigger coverage, runner/permission boundaries, and summary exit behavior. `CI Summary` uses `always()` and accepts only `success`: failure, cancellation, skipped, missing, and unknown baseline results are rejected. If the entire run is cancelled before the summary can run, cancellation is not successful qualification.

At issue #85 completion, this foundation did not aggregate the existing dbt workflow or run all application tests in CI. Issue [#86 now integrates offline dbt checks](issue-86-dbt-validation.md) into the aggregate and removes the separate `pr-validation.yml`. Documentation-link, domain metadata, broader Python and standards enforcement remain #87. GitHub branch protection and deployment controls remain #89 and #88. No protection settings, environments, credentials, or releases are changed by #85.

## Live execution evidence

Machine-readable evidence is in [issue-85-ci-execution.json](../evidence/phase-8/issue-85-ci-execution.json).

| Case | Source | Result |
| --- | --- | --- |
| Positive PR trigger | Draft [Phase 8 PR #122](https://github.com/Shreyash2942/FraudLens/pull/122), head `faaf28a`; [run 44435005871](https://github.com/Shreyash2942/FraudLens/actions/runs/44435005871). | Both baseline and summary passed; uploaded report is valid with no errors. This also proves draft PRs are not skipped. |
| Intentional negative PR trigger | Disposable draft [probe PR #123](https://github.com/Shreyash2942/FraudLens/pull/123); [run 44435087173](https://github.com/Shreyash2942/FraudLens/actions/runs/44435087173). | A malformed tracked Python file failed baseline validation; the report uploaded successfully and `CI Summary` failed rather than skipping or passing. |
| Negative report inspection | Downloaded failed-run artifact. | Exactly one `python_syntax` error at `scripts/ci/intentional_failure_probe.py`, line 1; the CI regression-test step itself passed. |
| Full local regression | Clean source archive of `faaf28a`, without private local configuration. | **82 tests and 133 subtests passed**. This broader suite was run manually for regression assurance; CI automation of that suite remains #87. |

The probe PR was closed without merging, and its remote/local branch and temporary worktree were removed. The malformed source never entered the Phase 8 branch. GitHub's PR refs retain the historical failed check as evidence.

The positive and negative runs execute the same workflow and validator implementation; the probe adds only the deliberate malformed file. The final documentation/evidence commit receives another normal PR run. A docs-only PR after merge is covered by the absence of path filters, but no isolated docs-only run on `main` is claimed before the new workflow merges.

## Reproduce locally and inspect GitHub

From a clean checkout, using Python 3.11 to match CI:

```powershell
py -3.11 -m pip install -r requirements-ci.txt
py -3.11 -m unittest discover -s tests/ci -p "test_*.py" -v
py -3.11 scripts/ci/validate_repository.py --report .ci-artifacts/repository-checks.json
```

An interpreter selected by `py` can also run the checks, but its version must be recorded; the live CI proof uses 3.11. The local report directory is ignored by Git.

```powershell
gh pr checks 122 --repo Shreyash2942/FraudLens
gh run view 44435005871 --repo Shreyash2942/FraudLens
gh run view 44435087173 --repo Shreyash2942/FraudLens --log-failed
```

For a future negative drill, use a disposable issue-linked branch and draft PR, introduce one malformed tracked source, verify baseline/report/summary behavior, then close without merging and remove only the probe resources. Do not add a permanent force-pass or force-fail workflow input.

The `push`-to-`main` path is configured and its filter is covered by regression tests; it has not run on `main` before merge. Manual `workflow_dispatch` likewise becomes available after the workflow exists on the default branch. Candidate packaging, release publication, and live runtime promotion are later workstreams.

The implementation follows GitHub's [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [trigger rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow), and [run-log inspection guidance](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs).
