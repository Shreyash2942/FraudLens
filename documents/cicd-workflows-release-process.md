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

## Environments and private configuration

The [portfolio environment contract](../.github/portfolio-environments.json) fixes `local_only_no_new_paid_resources` and `local_docker_operator`. Reuse the existing Data-Lab `fraudlens` container and persistent runtime volume; provision no paid cloud accounts, Snowflake compute, new containers, larger runners or public self-hosted runner. Test/prod names demonstrate governed controls, not three physical stacks.

| Environment | Runtime | GitHub protection |
| --- | --- | --- |
| `dev` | Existing local Docker, local Spark/Hive, isolated Airflow SQLite/SequentialExecutor metadata. | Only branch main; owner reviewer required, admin bypass disabled. Sole-owner self-review is permitted and explicitly identified as owner acceptance. |
| `test` | Disabled policy definition; no runtime paths, compute or credentials. | Only `portfolio-test-disabled` allowlist; no self-review, no admin bypass; workflow rejects target. |
| `prod` | Disabled policy definition; no runtime paths, compute or credentials. | Only `portfolio-prod-disabled` allowlist; no self-review, no admin bypass; workflow rejects target. |

The disabled allowlist strings do not create branches. Main also has required PR/conversation/CI controls. Default workflow tokens are read-only and cannot approve PR reviews; every external-contributor fork workflow requires owner approval. Public standard-runner guards are part of this portfolio's cost model; the scripts do not change billing settings or provision a cloud provider.

| Scope | Non-sensitive variables |
| --- | --- |
| Repository | `FRAUDLENS_COST_PROFILE=local_only_no_new_paid_resources`; `FRAUDLENS_DEV_DEPLOY_ENABLED=true` enables approved handoffs, not automatic Docker execution. |
| Dev policy | `FRAUDLENS_ENVIRONMENT=dev`, `FRAUDLENS_CLOUD_RESOURCES_ENABLED=false`, `FRAUDLENS_EXECUTION_MODE=local_docker_operator`. |
| Dev paths | `FRAUDLENS_DOCKER_CONTAINER=fraudlens`; `FRAUDLENS_DEPLOY_ROOT=/home/datalab/runtime/fraudlens/environments/dev`; `FRAUDLENS_RUNTIME_PYTHON=/usr/bin/python3`; `FRAUDLENS_SOURCE_ROOT=/home/datalab/fraudlens`. |
| Test/prod | Their environment identity; cloud false, execution mode disabled, `FRAUDLENS_DEPLOY_ENABLED=false`; no physical runtime configuration. |

GitHub requires **zero runtime secrets**. Its automatic read-only token accesses GitHub metadata/artifacts; it never supplies MongoDB/MinIO credentials to the runtime. Keep `FRAUDLENS_MONGODB_URI`, `DATALAB_MINIO_ACCESS_KEY` and `DATALAB_MINIO_SECRET_KEY` only in `<root>/secrets/runtime.json`, with a mode-`0700` managed root and mode-`0600` JSON owned by local `datalab`. The explicit allowlist includes local service endpoints and isolated Airflow settings; endpoint hosts must remain in the local sandbox. Use a separate Airflow database at `<root>/airflow/airflow.db`, not the legacy Data-Lab metadata store.

The regular marker `<root>/.fraudlens-runtime.json` must identify schema version 1, repository `Shreyash2942/FraudLens`, environment dev and profile local. Current DAGs use `<root>/current/airflow/dags`. Initial setup registered four paused DAG rows but activated no source or scheduler. Existing credentials are reused for this local portfolio; production account isolation or credential rotation is not claimed.

The following commands review GitHub setting plans without applying them:

```text
python -m scripts.deployment.environments --section definitions
python -m scripts.deployment.environments --section variables --enable-dev-handoff
python -m scripts.deployment.environments --section protections
```

Only append `--apply` after owner review of the intended section. Keep `--enable-dev-handoff` when intentionally enabling handoffs: variables applied without that option set the activation flag false. For a fresh local setup, inspect [the provisioning utility](../scripts/deployment/local_configuration.py) before running `python -m scripts.deployment.local_configuration`; it reads existing private local settings and initializes only the designated dev metadata/configuration store. Do not run setup as a routine deployment step or overwrite existing private settings to clear a failed gate.

Strict main status enforcement is **already applied**, verified after main run 45545800298. If restoring settings later, `python -m scripts.deployment.environments --section protections --seal-main --apply` first requires successful CI on actual current main and validates the Actions check identity. Feature-only evidence cannot seal main. Public variable changes after approval require a new configuration fingerprint/handoff. Rotate private credentials locally, preserve permissions and recheck authenticated service access; never publish values or hashes of secret values.

Ignore local `.env`, generator runtime configuration, `.ci-artifacts/` and generated batches. Preserve only sanitized report fields and credential **names** in public evidence. Avoid copying full environment dumps, connection exceptions, private configuration or service logs into GitHub issues/artifacts.

## Delivery checklist and evidence map

| Area | Evidence and acceptance |
| --- | --- |
| Baseline/dbt/Python validation | [#85 guide](phase-8-plan/issue-85-code-validation.md), [#86 guide](phase-8-plan/issue-86-dbt-validation.md), [#87 guide](phase-8-plan/issue-87-python-standards.md); dated run IDs, sanitized machine reports and deliberate failure propagation. |
| Immutable candidates | [#88 evidence](evidence/phase-8/issue-88-deployment-execution.json); preview integrity and promotion refusal. The original runner section is historical. |
| Environment controls | [#89 evidence](evidence/phase-8/issue-89-environment-controls.json); actual settings/private-permission/readiness audits and unsafe-cloud configuration rejection. Its pending status-seal field describes the earlier date. |
| PR pass/fail and local preflight | [#90 pre-merge evidence](evidence/phase-8/issue-90-premerge-validation.json); actual PR success/F821 failure, preview verification, actual operator refusal and read-only readiness. TCP checks are not pipeline semantics. |
| Merged main and strict gate | [Run 45545800298](https://github.com/Shreyash2942/FraudLens/actions/runs/45545800298), main `9080111`; baseline/dbt/Python/package/summary passed. Required strict `CI Summary`, app ID 15368, read back through GitHub API. |
| Remaining runtime/release evidence | Real owner-approved main handoff, local activation, fresh service/quality/pipeline success and controlled failure/recovery are not certified. No release/tag publication or production/Snowflake qualification is claimed. |

Issue #91 follows four task commits: CI purpose/triggers `dcdfd17`; deployment/release flow `af4f8f6`; environment/secrets handling `e4b4206`; README/index/current delivery updates in the containing fourth commit. Changes are documentation and policy status only; runtime/workflow implementation and secret values are excluded.

For a documentation contribution, stage new files, run repository/Markdown/contract validation, review commands against actual workflow inputs/CLI options, and require the PR's full `CI Summary`. This does not require executing deployment instructions, applying environment settings or publishing a release. Keep issue links/evidence dates current and distinguish verified behavior from future operational steps.
