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

## Deployment: candidate, approval, local activation

[`deploy.yml`](../.github/workflows/deploy.yml), named **Controlled Deployment**, has two routes:

1. CI's reusable `ci_bundle=true` route packages source only, including when CI itself was manually dispatched.
2. A standalone owner `workflow_dispatch` on main uses `operation=verify` or `deploy`. Only `dev` is implemented; test/prod fail preflight. Merging, tagging or successful CI does not automatically deploy.

Before dispatch, authenticate GitHub CLI as `Shreyash2942`, require completed successful main-**push** Code Validation for the selected full SHA/run/attempt, and inspect its candidate report. The SHA must be in main ancestry. Use the tar digest from that specific report, not the ZIP digest. Preflight independently verifies the repository/event/gates, current attempt, expiry, archive limits, existing protected dev environment, exclusive main branch policy and all digests. Missing settings/API access or a changed run attempt fails closed.

PowerShell example; replace the three selected values after inspecting the real main CI artifact:

```powershell
$candidateSha = 'FULL_40_CHARACTER_MAIN_CANDIDATE_SHA'
$ciRunId = 'SUCCESSFUL_MAIN_PUSH_RUN_ID'
$candidateDigest = '64_CHARACTER_CANDIDATE_TAR_SHA256'
gh workflow run deploy.yml --repo Shreyash2942/FraudLens --ref main -f operation=verify -f environment=dev -f candidate_sha=$candidateSha -f ci_run_id=$ciRunId -f candidate_sha256=$candidateDigest -f owner_approval=$candidateSha
```

Inspect the new **Controlled Deployment** run's `Verify Main Candidate` job and `deployment-verification-<run>-<attempt>` artifact. The success record has `deployment_executed=false`. After successful verification, explicitly request deployment with the same selection:

```powershell
gh workflow run deploy.yml --repo Shreyash2942/FraudLens --ref main -f operation=deploy -f environment=dev -f candidate_sha=$candidateSha -f ci_run_id=$ciRunId -f candidate_sha256=$candidateDigest -f owner_approval=$candidateSha
```

Identify that run using `gh run list --workflow deploy.yml --repo Shreyash2942/FraudLens`; inspect its inputs/source and complete **dev environment approval** in GitHub's run view. The repeated SHA is owner acceptance, not a substitute for environment review. Verify runs have no environment association. Deploy runs wait for owner review, disallow admin bypass, repeat preflight/configuration checks and serialize protected handoff jobs without cancelling an active job.

`Prepare Approved Dev Handoff` uploads only `dev-handoff-<deployment-run>-<attempt>` containing `handoff.json`. A green environment job means **approved handoff awaiting local operator**, not completed runtime deployment. It includes public configuration fingerprint, controller/candidate/run identities and `deployment_executed=false`.

On the owner machine, keep the existing `fraudlens` Docker container running. Its bind mount at `/home/datalab/fraudlens` must show a clean checkout of the **deployment workflow controller SHA**. This can differ from an older selected candidate SHA; inspect `gh run view <deployment-run> --json headSha`. Keep the runtime DAGs paused/drained and use the separately configured Airflow metadata store.

```text
python -m scripts.deployment.operator --deployment-run <approved-deployment-run>
python -m scripts.deployment.operator --deployment-run <approved-deployment-run> --apply
```

The first command verifies a plan without Docker activation. Run the second only after reviewing it. The operator requires a completed successful owner/main deployment workflow, explicit owner approval history, successful verify/handoff jobs, current-attempt artifact, unchanged public configuration, valid candidate CI and exact clean local controller. `flock -n <root>/.activation.lock` rejects concurrent local activation. Only public source/configuration enters Docker stdin; runtime credentials are loaded inside Docker and GitHub tokens are stripped before Airflow execution.

Activation stages verified source under `<root>/releases/<sha>-<digest-prefix>`, checks the local Spark/Hive profile and all four Airflow DAG imports against registered paused/drained metadata, then atomically updates `<root>/current`. Successful local output/report records `deployment_executed=true`, previous/current release and identity; save `.ci-artifacts/local-operator.json` with the corresponding CI/deployment reports. Activation does not start a scheduler or pipeline, migrate warehouse data or prove end-to-end analytics correctness.

## Retry, recovery and troubleshooting

| Symptom | Operator response |
| --- | --- |
| Failed/cancelled CI or required gate skipped | Inspect failed logs and sanitized gate report, fix source in a PR and obtain fresh successful main-push CI. Do not bypass `CI Summary`. |
| Preview/manual-CI run, wrong ref/actor/target, missing protections | Select a qualifying main-push run and owner main dispatch; inspect actual settings. Test/prod remain blocked. |
| Expired/missing artifact or superseded CI attempt | Qualify a fresh main-push candidate. A manually dispatched CI rerun is still a preview; rerunning the original push run changes its attempt, so obtain its new artifact/digest and fresh approval. |
| Changed environment configuration, controller checkout or approval | Obtain a new reviewed handoff; use the exact clean controller source and inspect environment settings. |
| Local lock busy | Let the active owner command finish. Do not remove a lock file to defeat a running holder. |
| Airflow import/maintenance failure | Active pointer stays unchanged. Inspect private local diagnostics without exporting credentials, repair the runtime dependency or paused/drained state, then reverify and retry the approved operation if still valid. |
| Modified release/unmanaged root/pending pointer | Stop for owner investigation. Do not overwrite or delete managed releases to force success. |

Repeating an unchanged verified candidate is idempotent. Prior releases are retained; choose a still-qualified compatible main candidate, or merge a revert/forward fix and requalify. A code-pointer change is not data rollback. Warehouse compatibility, restore plans and pipeline/service/quality/failure-recovery evidence require separate runtime qualification.

## Release record and publication

Release publication is a manual governed process; there is no automatic release workflow and a completed phase does not itself publish a release. The policy pattern is `v0.MINOR.PATCH` and names the qualified environment explicitly. No Phase 8 live runtime qualification or release publication is claimed here.

Before proposing a tag, preserve an evidence index with PR/commit SHA, main CI run/attempt, tar and ZIP digests, gate/dependency reports, environment/configuration fingerprint, owner acceptance/approval, deployment handoff identity and actual local activation/pipeline/service/quality outcomes. Record limitations and recovery compatibility. Include neither secret values nor generated banking datasets. Preserve required evidence within the 30-day artifact window in the approved evidence store.

After the owner accepts that evidence and release scope, create an annotated immutable version tag at the exact qualified SHA, push it, and prepare a GitHub **draft** release using that existing tag (`gh release create <tag> --verify-tag --draft --notes-file <evidence-notes-file>`). Review the named dev environment, evidence links and limitations before separately publishing. Never move/reuse a published tag or label local Spark/Hive evidence as a Snowflake production qualification. These are future operator instructions, not actions executed by this documentation task.
