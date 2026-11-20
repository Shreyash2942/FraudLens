# Issue #86: dbt validation in CI

Issue: [#86](https://github.com/Shreyash2942/FraudLens/issues/86)

Parent: [#83](https://github.com/Shreyash2942/FraudLens/issues/83)

Branch: `83-phase-8-cicd-implementation`

Validation date: November 19, 2026 (America/New_York; live runs use November 20 UTC)

The [Code Validation workflow](../../.github/workflows/ci.yml) now requires `dbt Validation` alongside `Baseline Repository Checks`. All PRs to `main`, including drafts and documentation changes, receive both checks. The resulting `main` commit is revalidated after merge. This implementation is on the phase branch until draft [PR #122](https://github.com/Shreyash2942/FraudLens/pull/122) merges.

## Priorities and task commits

| Priority | Issue task | Delivery |
| --- | --- | --- |
| 1 | Add dbt dependency installation | `f8f2efa`: Python 3.11, pinned dbt-core 1.8.7/dbt-hive 1.8.0, Kerberos build dependencies, `pip check`, version and adapter import checks. |
| 2 | Add dbt parse / compile checks | `a355f69`: full `dbt --no-partial-parse parse`, fixed CI Hive profile, fresh manifest, sanitized artifact. |
| 3 | Add dbt test or validation steps | `e28cd86`: both test selectors, five existing validators, empty-catalog docs, aggregate gate, regression tests, retirement of duplicate workflow. |
| 4 | Confirm failures block invalid changes | This evidence commit: passing and deliberately failing GitHub PR runs, report inspection, clean-source regression, documentation and graph refresh. |

## Validation sequence and boundaries

The dedicated [CI profile](../../dbt/profiles/ci/profiles.yml) contains a fixed loopback placeholder and no credential variables. CI starts no warehouse, accesses no deployment environment, and needs no Data-Lab, Snowflake, MinIO, or MongoDB secrets. Dependencies match the established Hive adapter generation; upgrading the runtime is separate work.

`scripts/ci/validate_dbt.py` removes any stale manifest, performs a full parse, and verifies a nonempty model/test manifest. The validation stage requires that successful parse and the identical manifest digest. It then:

1. Runs `dbt --quiet ls --resource-type test --selector ... --output json` for both `failure_blocking_gate` and `failure_diagnostic_gate`. Each must return actual, uniquely identified test records. Empty selection, log messages, invalid JSON, or non-test records fail instead of counting stdout lines as tests.
2. Runs the unchanged `validate_naming_rules.py`, `validate_governance_metadata.py`, `validate_contracts.py`, `validate_contract_alignment.py`, and `validate_failure_policy.py` against the fresh manifest, with the established selectors and failure-policy matrix.
3. Runs `dbt docs generate --empty-catalog --no-compile`, preserving docs generation without database introspection or SQL execution.

Each command must succeed. No stage uses `continue-on-error`. `CI Summary` uses `always()` and requires **both** job results to equal `success`; failure, cancellation, skip, missing and unknown results fail qualification. Regression tests execute the actual summary command for all 36 result combinations.

This satisfies the issue's **test or validation** option through offline validation. It does not execute warehouse-backed `dbt test`, validate runtime SQL semantics, or claim compiled SQL. dbt recommends [parse for warehouse-free validation](https://docs.getdbt.com/reference/commands/parse); [list resolves selectors without queries](https://docs.getdbt.com/reference/commands/list), while [compile can need a warehouse](https://docs.getdbt.com/reference/commands/compile). Runtime build/data-test qualification stays in the deployment and end-to-end workstreams (#88/#90). Enforced merge protection remains #89; failing CI is verified here, but protection settings are not configured by #86.

Only `.ci-artifacts/dbt-validation.json` is uploaded for 30 days, including on validation failure. It records stage/check outcomes, selector counts, manifest digest/counts, dbt dependency versions, tested merge SHA, PR head SHA, run/attempt, and timestamp. SQL, manifests, connection profiles, source data, logs, and credentials are excluded from this artifact. Dependency-install failure still fails the job even when no report can be created.

## Execution evidence

Machine evidence: [issue-86-dbt-execution.json](../evidence/phase-8/issue-86-dbt-execution.json).

- Passing phase PR: [run 44653554383](https://github.com/Shreyash2942/FraudLens/actions/runs/44653554383), source `e28cd86`. The manifest contains 61 models and 183 tests; the blocking and diagnostic selectors resolve to 143 and 183 tests respectively. Both stages and all eight validation checks passed.
- Missing reference: [run 44653628665](https://github.com/Shreyash2942/FraudLens/actions/runs/44653628665), source `f5cf096`. Parse failed, later validation was skipped, and no stale manifest was reported. Baseline passed, dbt and summary failed, and the failure report uploaded.
- Invalid alias: [run 44653868155](https://github.com/Shreyash2942/FraudLens/actions/runs/44653868155), source `144dd82`. Parse and both selectors passed; naming rejected `INVALID_CI_ALIAS`. Later validators/docs did not run. Baseline passed, dbt and summary failed, and the failure report uploaded.
- Clean source archive of `e28cd86`: **88 tests and 168 subtests passed**, including 17 CI regression tests. This full suite is manual regression evidence; automatic broader Python/domain coverage remains #87.

Both controlled failures used disposable [PR #124](https://github.com/Shreyash2942/FraudLens/pull/124), now closed without merging. Its remote/local branch and temporary worktree were removed. The invalid changes never entered the phase branch. The final evidence commit receives a fresh PR run. Main-push validation and manual dispatch are configured; their execution on the default branch is not claimed before merge.

## Reproduce

On a clean Ubuntu checkout with Python 3.11:

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y krb5-user libkrb5-dev
python -m pip install -r requirements-ci.txt -r requirements-dbt-ci.txt
python -m pip check
python -m unittest discover -s tests/ci -p 'test_*.py' -v
python scripts/ci/validate_dbt.py --stage parse
python scripts/ci/validate_dbt.py --stage validate
```

Use a disposable branch/PR for a failure drill: add a model with a missing `ref` to prove parse rejection, or add an uppercase alias to an existing governed model to prove post-parse validator rejection. Verify baseline success, dbt failure, summary failure, and report upload; close without merging and remove the probe branch/worktree.
