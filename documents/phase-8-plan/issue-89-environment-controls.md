# Issue #89: portfolio environment controls and local secrets

Issue: [#89](https://github.com/Shreyash2942/FraudLens/issues/89)

Parent: [#83](https://github.com/Shreyash2942/FraudLens/issues/83)

Branch: `83-phase-8-cicd-implementation`

Configuration date: November 22, 2026 (America/New_York; execution timestamps may use November 23 UTC)

## Portfolio model and task delivery

The [environment contract](../../.github/portfolio-environments.json) implements the owner's no-spend requirement. The repository is public, runner jobs use standard Ubuntu 24.04, and provider/cloud activation is disabled. The project reuses the existing `fraudlens` Data-Lab Docker container/image and its `datalab-runtime-fraudlens` volume. No cloud accounts, Snowflake compute, new containers, larger runners or billing changes are provisioned.

| Task | Commit and outcome |
| --- | --- |
| 1. Define environment structure | `4cbaf6f`: versioned local-only contract and three GitHub environment definitions, with owner review from creation. |
| 2. Configure secrets and variables | `22142d0`: scoped non-sensitive GitHub variables; private dev configuration on the existing Docker volume; separate Airflow metadata and paused DAG registrations. |
| 3. Apply protection | `afe3e79`: main PR/conversation/admin controls, force/deletion prevention, strict environment branch restrictions, read-only default tokens and approval for every external contributor's fork workflow. |
| 4. Consume configuration safely | This commit: hosted approval handoff, explicit local Docker operator, approval/digest/configuration checks, token isolation, public/free-runner policy audit, tests and execution evidence. |

| Environment | Resources and controls |
| --- | --- |
| `dev` | One existing local Docker runtime; main-only GitHub deployments, required owner reviewer, admin bypass disabled. Self-review is allowed for this sole-maintainer portfolio and is recorded as owner acceptance, not independent review. |
| `test` | Disabled policy definition, no runtime/endpoints/secrets. Branch allowlist is `portfolio-test-disabled`; self-review is prohibited and the workflow has no execution path for this target. |
| `prod` | Disabled policy definition, no runtime/endpoints/secrets. Branch allowlist is `portfolio-prod-disabled`; self-review is prohibited and the workflow has no execution path for this target. |

The unused branch names do not create branches or compute. Separate environment names demonstrate promotion/control design without pretending that three physical production-grade stacks exist. Snowflake remains an architectural target rather than a provisioned service.

GitHub documents standard public-repository runners as free and makes environment review/protection available for public repositories. These are the features used here; private-repository execution is outside this portfolio policy and runner jobs have public-only guards. See [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) and [environment availability](https://docs.github.com/en/rest/deployments/environments).

## Secrets stay local

GitHub needs **zero runtime secrets**. Its automatic token is read-only and is used only for candidate/protection metadata and artifacts. The new workflow does not refer to `secrets.*`, inherit runtime secrets, register a self-hosted runner, expose Docker, or transmit local credentials to GitHub.

The dev secret store is `/home/datalab/runtime/fraudlens/environments/dev/secrets/runtime.json` in the existing persistent volume. The private directory is mode `0700`, the JSON file mode `0600`, and operations run as `datalab`. It contains curated MongoDB/MinIO settings from the existing local configuration plus isolated Airflow settings. Only required key names, permission results and connection-probe booleans enter public evidence; values and hashes of secret values are excluded. The legacy ignored generator configuration is not copied into candidates or sourced by a shell.

Required local names are `FRAUDLENS_MONGODB_URI`, `DATALAB_MINIO_ACCESS_KEY` and `DATALAB_MINIO_SECRET_KEY`; endpoints are restricted to the local sandbox. Read-only checks confirmed authenticated MongoDB ping and MinIO bucket access. Existing credentials are reused for the local portfolio; this does not claim production credential rotation or enterprise service-account isolation.

Airflow 2.9.3 uses a new metadata database under the dev root, SQLite/SequentialExecutor, four paused FraudLens DAG registrations and no running scheduler/pipeline. The existing Data-Lab Airflow metadata/service configuration is preserved. No candidate source is activated by configuration setup; actual source activation and pipeline qualification remain #90.

## Applied GitHub settings

The configuration utility uses authenticated GitHub CLI REST calls. Its default is a reviewable plan; `--apply` makes the explicitly requested settings changes. It verifies a public repository and never calls cloud-provider APIs:

```bash
python -m scripts.deployment.environments --section definitions
python -m scripts.deployment.environments --section variables
python -m scripts.deployment.environments --section protections
```

Apply only the needed section with `--apply`. Reapplying definitions preserves existing branch policy selection, and reapplying protections preserves already enforced required status checks. The dev environment allows only branch `main`, requires the owner reviewer and disallows administrator bypass. Test/prod are separately locked as described above.

Repository variables are `FRAUDLENS_COST_PROFILE=local_only_no_new_paid_resources` and `FRAUDLENS_DEV_DEPLOY_ENABLED=true`. The latter enables approval handoffs; it neither starts Docker nor triggers a deployment automatically. Environment variables identify execution mode, local container, managed root, runtime Python, source root and `FRAUDLENS_CLOUD_RESOURCES_ENABLED=false`. They contain no connection credentials. Disabled targets have `FRAUDLENS_DEPLOY_ENABLED=false` and no physical runtime configuration.

Main protection requires a PR and resolved conversations, enforces administrators and forbids force pushes/deletion. The approving-review count is zero for a sole owner who cannot independently approve their own PR; the owner records acceptance at merge. Stale reviews are dismissed. Default workflow tokens are read-only, cannot approve PR reviews, and all external-contributor fork workflows require owner approval.

**Required status activation is deliberately deferred:** main still contains the pre-Phase-8 baseline. A passing feature-branch check is not proof of the actual main commit. After reviewed phase merge and a successful push-to-main Code Validation run, execute:

```bash
python -m scripts.deployment.environments --section protections --seal-main --apply
```

This verifies the actual current main SHA, successful main workflow/gates and the GitHub Actions check identity before requiring up-to-date `CI Summary`. It refuses feature-only evidence. Until that step, required status checks are not claimed as enforced; the PR/main protection and environment protections above are already applied. The phase PR remains draft until its review/merge is appropriate.

## Approved handoff and local operation

The original #88 self-hosted deployment job is replaced by a standard hosted **Prepare Approved Dev Handoff** job. Public CI only packages source; `ci_bundle=true` prevents it from entering protected jobs, including manually dispatched CI. A standalone main deployment dispatch must select the full main candidate SHA, successful push-to-main CI run/attempt, tar digest and repeated owner acceptance SHA.

Preflight verifies repository visibility/cost mode, provenance, required gates, main ancestry, artifact/ZIP/tar/file hashes, existing environment review policy and main-only restriction. The protected handoff job waits for environment approval, repeats verification, checks exact non-sensitive configuration against the contract and emits only `handoff.json`. A green GitHub environment job means **handoff approved**, not runtime already deployed.

After the reviewed main workflow exists and a valid candidate is selected:

1. Dispatch `deploy.yml` on `main` with `operation=deploy`, target `dev` and the exact candidate/run/digest/acceptance inputs; complete the owner environment approval.
2. Use a clean local checkout matching the deployment workflow run's head SHA, mounted at the existing container's `/home/datalab/fraudlens`. Inspect it with `gh run view <deployment-run> --json headSha`.
3. Verify the handoff locally; default mode makes no Docker changes:

```bash
python -m scripts.deployment.operator --deployment-run <approved-deployment-run>
```

4. After inspection, explicitly activate that same approved handoff locally:

```bash
python -m scripts.deployment.operator --deployment-run <approved-deployment-run> --apply
```

The operator requires authenticated owner identity, a completed successful main deployment workflow, owner approval history, successful protected jobs and an unexpired current-attempt handoff artifact. It checks configuration fingerprints, reruns candidate/protection verification, verifies the clean local controller commit and sends only public bundle/configuration data to Docker stdin. GitHub tokens are never forwarded to Docker or the Airflow subprocess.

Local activation runs under the existing container's nonblocking `flock` on `<root>/.activation.lock`. A concurrent owner command stops instead of overlapping activation; the OS releases the lock when the process exits. GitHub concurrency separately serializes approval handoff jobs.

Inside Docker, the private JSON is loaded through an explicit key allowlist; no `source .env` or free-form command is accepted. Nonlocal endpoints, wrong permissions, wrong metadata database, changed controller/root or missing secrets stop execution. The existing managed activation implementation then verifies source again, checks Airflow imports and paused/drained DAGs, and atomically switches the active code pointer. A failed import preserves the previous pointer. This does not start a scheduler, run a pipeline, migrate warehouse data or perform data rollback.

## Validation, evidence and remaining boundary

The local regression suite passes with the two Linux-only activation tests skipped on Windows. Hosted Linux validates those tests as well. New tests reject cloud policy, paid/self-hosted runner declarations, unpinned actions, runtime-secret references, missing/forged approvals, changed configuration and wrong controller identity. They also prove plan-by-default behavior and that token canaries never enter Docker or Airflow transport.

The offline `python -m scripts.deployment.environment_audit` is now a required repository CI step. It checks local-only policy, standard public runner guards, read-only tokens, pinned actions, no runtime-secret references and separation of packaging from the protected handoff. It performs no network writes or Docker calls. Real GitHub settings and the local private-store/metadata/service checks are captured separately in sanitized machine evidence.

Machine evidence: [issue-89-environment-controls.json](../evidence/phase-8/issue-89-environment-controls.json).

| Check | Recorded outcome |
| --- | --- |
| Valid configuration | [Run 45086588170](https://github.com/Shreyash2942/FraudLens/actions/runs/45086588170): baseline, dbt, Python, candidate packaging and summary passed; dispatch-only verification/handoff stayed skipped. Hosted Python 3.11.18 passed **123 tests and 1,471 subtests**, including 52 CI tests and both Linux activation tests, with no skips. All 147 tracked Python files passed lint. |
| Unsafe configuration | [Run 45087263173](https://github.com/Shreyash2942/FraudLens/actions/runs/45087263173): the actual handoff configuration validator first accepted the valid control, then rejected the same configuration with only cloud enablement changed. Baseline and summary failed; dbt/Python passed, deployment was skipped and the rejection artifact records no Docker execution. |
| Artifact integrity | GitHub ZIP digest, candidate tar and every source-file digest downloaded and verified. Preview artifacts contain public committed source, no private runtime configuration, and cannot qualify for promotion. The evidence separates the tested blob hashes from a final operator-context follow-up and its expected hashes; the final commit receives fresh normal phase-PR CI and artifact inspection. |
| Applied controls | Actual dev/test/prod settings, repository variables, read-only token/fork approval policy and main protection were read back through GitHub APIs. Main's required status context remains explicitly pending post-merge sealing. Local checks confirmed `0700` root/`0600` secrets, authenticated MongoDB/MinIO access, four paused isolated DAG rows, zero runs and no active source pointer. |
| Cleanup | Disposable [PR #127](https://github.com/Shreyash2942/FraudLens/pull/127) closed without merge; its temporary worktree and local/remote branch removed. The phase branch contains no deliberate failure probe. |

Final review found that the local operator must explicitly pass `TARGET_ENVIRONMENT=dev` into the shared dispatch guard. The adapter now supplies it, its approved-handoff test calls the real guard at that boundary, and local activation uses the existing container's `flock` to reject concurrent execution. This follow-up preserves the test count and is covered by final-commit CI; the earlier probe is not presented as testing these two changed blobs. A separate disposable lock-contention/release probe validates the container utility without activating source.

No paid resources, cloud accounts, new containers, self-hosted runners, runtime source activation, scheduler starts, releases or main merges are claimed. #89 delivers controls/configuration. Post-merge status sealing, approved real runtime deployment and end-to-end service/quality/failure/recovery proof remain part of #90; #91 supplies the final handoff.
