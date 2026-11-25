# Issue #88: controlled deployment workflow

Issue: [#88](https://github.com/Shreyash2942/FraudLens/issues/88)

Parent: [#83](https://github.com/Shreyash2942/FraudLens/issues/83)

Branch: `83-phase-8-cicd-implementation`

Validation date: November 21, 2026 (America/New_York; GitHub runs use November 22 UTC)

Current operation is defined by [#89 environment controls](issue-89-environment-controls.md). Its no-spend portfolio model replaces the original self-hosted runtime job with an approved hosted handoff and explicit local Docker operator. The execution and evidence below describe #88 as delivered; follow #89 for current configuration and commands.

## Delivery priorities and task commits

| Task | Delivery |
| --- | --- |
| 1. Create deployment workflow file | `4786c52`: reusable/manual `deploy.yml`, pinned checkout/setup, hosted candidate job and explicit inputs. |
| 2. Define deployment trigger conditions | `dbf3f2e`: immutable bundles, archive/file digests, main CI/provenance and environment preflight, owner dispatch, preview isolation and the fourth CI gate. |
| 3. Align deployment with environment model | `811678e`: protected dev job, managed local runtime adapter, serialized activation, import/maintenance gates, recovery records and deployment regression tests. |
| 4. Validate deployment execution path | This evidence commit: real GitHub packaging and rejection runs, downloaded artifact verification, hosted Linux activation fixtures, documentation and graph refresh. |

The [release model](../cicd-strategy-release-model.md) permits #88 development and dry-run validation alongside #89. This delivers the workflow implementation on the phase branch. **Live dev activation is blocked until #89 configures controls and trusted infrastructure and the workflow merges to main.** Actual Airflow/Data-Lab pipeline success, quality gates, failure/recovery and service evidence belong to #90. No environments, settings, credentials, runners, services, releases or main merges were created by #88.

## Candidate lifecycle and trigger conditions

The [Code Validation workflow](../../.github/workflows/ci.yml) invokes [deploy.yml](../../.github/workflows/deploy.yml) only after baseline/standards, Python and dbt succeed. It supplies the typed `ci_bundle=true` input, including for manually dispatched CI runs. The reusable path builds and verifies a candidate; it never associates a GitHub environment or schedules the privileged runner. Only the standalone deployment dispatch with packaging mode absent can enter preflight/deployment. `CI Summary` requires packaging as a fourth gate and its regression test executes all 1,296 gate-result combinations.

`scripts/deployment/candidate.py` requires clean tracked source and baseline validation, reads committed regular Git blobs, rejects symlinks/submodules and private/generated tracked inputs, and writes three files: `candidate.tar`, `candidate.sha256` and `candidate-report.json`. The tar contains a provenance manifest and exact source payload with per-file SHA-256 and executable modes. Verification rejects archive traversal, links, duplicate/extra/missing files, changed hashes and mismatched identities. Size and inventory limits apply. Ignored private configuration and generated data never enter the source inventory.

The artifact name includes full source SHA, workflow run and attempt. A PR source is the tested merge SHA and is marked `preview_only`; renaming that bundle does not qualify it for promotion. A push to main is marked `await_completed_main_ci`, and can be selected only after that entire CI run succeeds. Packaging is not deployment. The candidate report/Actions summary supplies the tar SHA-256; GitHub separately records the outer artifact ZIP digest. Bundles/reports are retained for 30 days. Release retention/publication remains the later handoff.

Manual `workflow_dispatch` offers `verify` and `deploy`. Both require:

- Owner dispatch from `refs/heads/main` and repository activation variable `FRAUDLENS_DEV_DEPLOY_ENABLED=true`.
- Target `dev`, a full 40-character main candidate SHA, a positive CI run ID, the 64-character tar SHA-256, and `owner_approval` repeating that exact SHA. Cloud targets remain rejected.
- A completed successful `push` to main from `ci.yml`, matching repository/SHA, successful baseline/dbt/Python/summary jobs and main ancestry. PR, feature, failed, cancelled, missing, diverged and mismatched evidence cannot qualify.
- An existing dev environment with admin bypass disabled, the owner as a required user reviewer and an exclusive custom `main` branch deployment policy. HTTP 403/404 is rejection, not permission to create settings.
- The exact current run-attempt artifact, unexpired and within size limits; matching GitHub ZIP digest, operator-selected tar digest, manifest run/attempt/source and every file digest. Preview bundles are rejected again after download.

The hosted preflight has no environment association and makes only read API calls. `verify` stops after producing a sanitized plan. `deploy` then waits for GitHub's environment approval and obtains the trusted runner. The runtime job repeats preflight after approval/queueing so changed controls, expired artifacts and superseded attempts cannot reuse a stale plan. Workflow inputs enter commands through environment variables; there is no free-form shell-command or ref override input.

After merge, with a real successful push-to-main candidate and #89 ready:

```bash
gh workflow run deploy.yml --ref main \
  -f operation=verify -f environment=dev \
  -f candidate_sha=<full-main-sha> -f ci_run_id=<main-ci-run-id> \
  -f candidate_sha256=<tar-sha256> -f owner_approval=<same-main-sha>
```

Inspect verification, then dispatch `operation=deploy` with the same candidate/digest and complete the environment approval. This dispatch path is intentionally unavailable on the default branch before the Phase 8 workflow merges. Merging or tagging never triggers automatic runtime deployment.

## Historical dev runner design, superseded by #89

The original #88 implementation used `[self-hosted, linux, fraudlens-dev-deploy]`. **Do not provision that runner.** The [#89 environment controls](issue-89-environment-controls.md) supersede this design: protected standard-hosted execution produces an approved handoff, and an explicit owner-operated local Docker command consumes it. No public workflow executes on the developer container. The following table records the original #88 prerequisites; use the #89 guide for current paths, private configuration and operator commands.

GitHub configuration expected from #89:

| Location | Setting |
| --- | --- |
| Repository variable | `FRAUDLENS_DEV_DEPLOY_ENABLED=true`, only after controls/infrastructure are verified. Missing/false stays blocked. |
| Existing dev environment | Owner reviewer, admin bypass disabled, custom branch restriction allowing only branch `main`. Owner approval is self-review, not independent review. |
| Environment variable | `FRAUDLENS_DEPLOY_ROOT`, absolute managed directory such as `/srv/fraudlens`; not the checkout, filesystem root or an existing legacy repo directory. |
| Environment variable | `FRAUDLENS_RUNTIME_PYTHON`, absolute interpreter path in the separately managed Airflow runtime; it must have access to the same release paths. |
| Private runtime configuration | Required database/artifact/lineage/service credentials provisioned by #89 and available to the trusted runtime; no credential values enter source bundles or reports. This code deployment does not install or replace a service's credentials/dependencies. |

Explicitly provision the root and this regular marker file `.fraudlens-runtime.json`:

```json
{"schema_version": 1, "repository": "Shreyash2942/FraudLens", "environment": "dev", "profile": "local"}
```

Configure the Airflow service to use `<root>/current/airflow/dags` and `FRAUDLENS_REPO_ROOT=<root>/current`; retain the runtime's private settings outside the release source. Register and pause all four FraudLens DAGs and drain running/queued runs before activation. Keep the maintenance window closed to new triggers throughout deployment. #88 does not migrate or overwrite the existing `/home/datalab/fraudlens` installation or edit scheduler configuration automatically.

## Activation, retry and recovery behavior

`scripts/deployment/runtime.py` accepts only a managed Linux dev/local target. It verifies the bundle again, checks the local Spark/Hive profile, and stages exact source under `<root>/releases/<sha>-<digest-prefix>`. Existing candidates must match their recorded identity and source inventory; altered files or unmanaged destinations fail instead of being overwritten.

Before activation, a fixed subprocess in the separate Airflow interpreter imports the candidate's DAG folder, requires all four expected DAG IDs and no import errors, and checks the Airflow metadata store for registered, paused DAGs with no running/queued runs. It neither runs a DAG nor queries the warehouse. Import/query failure stops activation. Only success atomically replaces `<root>/current` with a symlink to the verified release. Scheduling and actual data execution remain paused for the controlled #90 qualification.

The result records candidate/run identity, actor, previous/current release, runtime path fingerprint and import/maintenance outcome. Repeating an unchanged candidate is idempotent. Failed import preserves the prior active pointer; a retry can activate the staged candidate after the issue is repaired. Modified source or unexpected files require investigation. Per-environment GitHub concurrency serializes runtime jobs and never cancels an active deployment for a newer candidate.

Prior releases are retained; no automatic data or code rollback is attempted. The owner chooses a compatible prior qualified candidate within artifact retention, or qualifies a new main revert/forward-fix commit. Warehouse schema/data compatibility and fresh runtime qualification are required separately. Merely switching code is not data rollback.

## Validation and boundaries

Initial pinned-environment regression: **109 tests and 1,451 subtests passed; two Linux-only filesystem activation tests skipped on Windows**. The hosted Linux run exercises those tests, including idempotency, a new candidate's failed import preserving the prior pointer, recovery, unmanaged-directory refusal and modified-release rejection. GitHub/API and Airflow outcomes in these isolated tests use fixtures; they do not claim a live Data-Lab activation or environment approval.

The evidence records actual reusable-workflow packaging, archive inspection and a controlled PR-context rejection that must fail deployment validation and CI Summary. Actual post-merge dispatch, environment approval, trusted runner activation and live Airflow import/pipeline checks remain pending #89/main merge/#90. Missing prerequisites remain blocking; no force-pass switch is provided.

Machine evidence: [issue-88-deployment-execution.json](../evidence/phase-8/issue-88-deployment-execution.json).

| Case | Evidence |
| --- | --- |
| Reusable workflow success | [Run 44970010277](https://github.com/Shreyash2942/FraudLens/actions/runs/44970010277), source `811678e`: all required checks and Candidate Bundle passed; dispatch-only jobs were explicitly skipped. The preview contains 618 verified source files and is marked non-deployed/unqualified for promotion. |
| Artifact integrity | Downloaded GitHub ZIP digest matched API metadata; tar digest and every manifest file hash verified. No private config or generated data paths were in the payload. The evidence records tested merge blob digests and identifies the final packaging-mode routing/test follow-up separately. |
| Hosted regression | Python 3.11.18: **111 tests and 1,451 subtests passed**, including 40 CI tests, all 1,296 aggregate combinations and both Linux filesystem activation/recovery tests. Sanitized JUnit contains 1,562 successful records and no failures/errors/skips. Airflow/API outcomes in isolated tests are fixtures. |
| PR promotion rejection | [Run 44970295561](https://github.com/Shreyash2942/FraudLens/actions/runs/44970295561), source `30606d2`: invoking the actual preflight from PR context failed Candidate Bundle and CI Summary. Baseline/dbt/Python passed; protected jobs stayed skipped. The uploaded report records rejection and `deployment_executed=false`. |
| Cleanup and control boundary | Disposable [PR #126](https://github.com/Shreyash2942/FraudLens/pull/126) closed without merge; its remote/local branch and temporary worktree were removed. GitHub environment inventory remained empty before/after. The phase branch contains no intentional failure. |

Final review added explicit packaging-mode routing and tests for manually dispatched CI, since CI and deployment otherwise share GitHub's dispatch event. Local follow-up regression passed **109 tests and 1,453 subtests with two Linux-only skips**. The final evidence commit receives a fresh normal PR run, with its final candidate artifact verified before closure. This issue closes implementation delivery on the phase branch; it does not certify live activation, close #89/#90 or close the Phase 8 parent.

References: [GitHub reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows), [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [environment API](https://docs.github.com/en/rest/deployments/environments) and [artifact API](https://docs.github.com/en/rest/actions/artifacts).
