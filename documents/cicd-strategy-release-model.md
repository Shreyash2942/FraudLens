# CI/CD strategy and release model

Issue: [#84](https://github.com/Shreyash2942/FraudLens/issues/84)  
Parent: [#83 — Phase 8: CI/CD Implementation](https://github.com/Shreyash2942/FraudLens/issues/83)  
Decision date: November 17, 2026

This is the agreed design for validation, merge, promotion, and release control. The machine-readable operational contract is [`.github/cicd-release-contract.yaml`](../.github/cicd-release-contract.yaml). Issue #84 defines the operating model; issues #85–#91 implement and prove its controls.

Portfolio constraint updated November 22, 2026 under [#89](phase-8-plan/issue-89-environment-controls.md): provision no paid cloud resources. Only the existing local Docker dev runtime is active infrastructure; GitHub test/prod are disabled policy definitions. Standard public Ubuntu CI prepares an approved handoff, and the owner executes it locally. The initial self-hosted-runner implementation from #88 is superseded by this local-operator path. Snowflake remains the conceptual analytics target; no Snowflake or other cloud account is provisioned for this portfolio.

## Priorities and task commits

| Order | Priority | Issue #84 task | Commit scope |
| --- | --- | --- | --- |
| 1 | P0 | Define CI goals and release flow | Validation gates, candidate identity, release evidence, and failure behavior. |
| 2 | P0 | Define branch and merge expectations | Branch ownership, pull requests, review, merge gates, and exceptions. |
| 3 | P0 | Define promotion path across environments | Secret-free CI, Data-Lab runtime checks, and optional Snowflake qualification. |
| 4 | P1 | Align strategy with milestones and delivery needs | Implementation dependencies, acceptance evidence, and Phase 9 handoff. |

The three P0 decisions establish the control boundaries before workflow implementation. Each task has one focused commit referencing #84.

## 1. CI goals and release flow

### Observed baseline

At the Phase 8 baseline, `main` contains merged Phase 7 at `0be6db2`. The [baseline PR workflow](https://github.com/Shreyash2942/FraudLens/blob/0be6db22652c135df81aaad885e251a52d1bf314/.github/workflows/pr-validation.yml) runs `dbt Structure Validation` for changes under `dbt/` or its own workflow file. It performs dbt parsing, selector/governance/contract validation, and empty-catalog documentation generation using Python 3.11, dbt-core 1.8.7, and the Hive adapter. Issue #86 migrates these offline checks into `ci.yml` and its aggregate gate; see the [implementation guide](phase-8-plan/issue-86-dbt-validation.md).

The workflow does not yet provide repository-wide Python/standards checks, post-merge candidate validation, deployment, or release packaging. Read-only GitHub inspection on the decision date found no `main` branch protection or repository rulesets, no configured GitHub environments, and no published GitHub releases. These are baseline observations, not claims that the target policy is already enforced.

### Validation goals and gates

| Gate | Required outcome | Evidence | Implementation owner |
| --- | --- | --- | --- |
| Repository standards | Markdown links and YAML parse; governed naming, ownership, controls, and contracts remain aligned. | Validation log and structured findings. | #85, #87 |
| Python validation | Relevant generator, helper, observability, and Airflow scaffold tests pass in a clean workspace. | Test report tied to the tested commit. | #85, #87 |
| dbt validation | Parse, selectors, naming, governance metadata, contracts, failure policy, and empty-catalog docs pass. | Manifest and validator summaries. | #86 |
| CI Summary | Every applicable gate succeeds; an error, cancellation, missing result, or unjustified skip fails the summary. | Stable aggregate check with explicit applicability decisions. | #85 |

`CI Summary` is the proposed required merge check. The workflow must run for every pull request to `main`; individual jobs may classify changes, but workflow-level path filtering must not suppress the required summary. A docs-only change still runs standards/link/YAML validation and the summary. Runtime tests may be explicitly inapplicable with a recorded reason; a missing check is never evidence of success.

Use ephemeral GitHub-hosted runners for untrusted pull-request code, repository-content read permissions, and no deployment credentials. Do not execute untrusted pull-request revisions in privileged `pull_request_target` jobs or on the developer's persistent Data-Lab runner. Pin supported runner/dependency versions during implementation and record them with each run.

CI must start without ignored private `.env`, `synthetic_generator/runtime_config.yaml`, generated batches, dbt targets, or cached credentials. Cache dependency downloads only; do not reuse local data or a previous validation result. The Phase 7 clean-worktree baseline was 71 tests and 127 subtests; this is historical evidence, not a permanent test-count requirement.

### Candidate and release lifecycle

1. Develop and validate locally on an issue-linked branch.
2. Open a pull request to `main`; run secret-free checks against the pull-request merge candidate. Record both the head SHA and tested merge SHA.
3. Review and merge only after all applicable checks pass for the current revision.
4. Revalidate the resulting `main` commit. A passing pull-request SHA alone does not qualify a different merge commit.
5. Produce a candidate bundle identified by the full `main` commit SHA and workflow run/attempt. Include file digests and validation reports. A candidate is not a deployment.
6. Explicitly select that same candidate for runtime promotion. Reject arbitrary feature refs, altered artifacts, stale evidence, and changed configuration that lacks revalidation.
7. After required runtime checks and approval, create a protected, immutable release tag and GitHub release referring to that verified `main` commit. The release record identifies exactly which environment was validated.

Use `v0.MINOR.PATCH` for portfolio releases: increment MINOR for an accepted capability increment and PATCH for a compatible corrective release. Record incompatible contract changes explicitly in release notes and plan migration; a version number never substitutes for contract review. A phase boundary does not automatically publish a release, and no release tag is created by issue #84.

The candidate bundle must contain the commit SHA, pull request, workflow run/attempt, dependency versions, manifest and package digests, gate outcomes, configuration fingerprint without secrets, release notes, and operator owner. Runtime promotion adds environment identity, approver, batch/run IDs, smoke and quality results, metric/lineage evidence, and any accepted limitations. Keep reports for at least 30 days and retain a sanitized evidence index plus artifact checksums in the GitHub release record; secrets and generated banking data stay out of the bundle.

### Failure, retry, and recovery

- A failed or cancelled mandatory check blocks merge qualification and promotion. A retry may repair infrastructure failure, but must run against the same candidate and create a new run/attempt record.
- A new commit, manifest change, dependency change, or material environment/configuration change invalidates prior qualification. Build a new candidate and repeat affected checks.
- Serialize deployment per environment; do not cancel a deployment mid-migration to make way for a newer candidate. Pull-request checks may cancel superseded runs.
- On failed runtime verification, stop promotion and capture evidence. Restore the prior verified code/configuration candidate only when the operator confirms compatibility. Warehouse data/schema changes require a documented restore or forward-fix decision; checking out old code does not roll back data.

## 2. Branch and merge expectations

### Branch lifecycle

- `main` is the integration and candidate source branch. Feature branches start from current `origin/main` and use `NN-short-slug`, with the issue number in commits and the pull request.
- Phase-wide branches may use the parent issue number. The existing `83-phase-8-cicd-implementation` branch groups Phase 8 work; issue #84 contributes four task commits to it. Closing #84 records design delivery on this branch, not a merge of the complete phase.
- There is no permanent `develop`, `test`, or `prod` code branch. Promote an identified `main` candidate through environment gates instead of copying code between environment branches.
- Preserve the task history with a merge commit for the phase pull request. Small corrective pull requests may use another documented merge method only when issue/commit traceability remains intact.
- Synchronize changes from `main` and rerun qualification after conflict resolution. Avoid rewriting a branch under active review. An explicitly agreed rewrite requires a backup, `--force-with-lease`, and fresh checks; never force-push `main` or move an existing release tag.

### Merge policy and enforcement handoff

| Requirement | Policy | Enforcement owner |
| --- | --- | --- |
| Pull request | All ordinary changes to `main` use an issue-linked PR with scope, validation, control impact, and known limitations. | #85, #89 |
| Current checks | The latest tested revision must have a successful `CI Summary`; resolve relevant failed checks and conversations. A newly changed revision invalidates older evidence. | #85–#87, #89 |
| Review | With another qualified maintainer, require an independent approval and dismiss stale approval after material changes. A sole maintainer records the review checklist and explicit owner acceptance in the PR; this is self-review, not independent approval. | #89 |
| Protected integration | Require PRs, passing aggregate checks, up-to-date integration, and resolved conversations; restrict deletion and force pushes, including administrative bypass where supported. | #89 |
| Check availability | Enable required status contexts only after the jobs exist on `main` and their exact names are verified. Path-specific checks cannot be the only required workflow. | #85, #89 |
| Release changes | Changes to workflows, contracts, environment controls, or release logic receive an explicit control-impact review even when no runtime code changes. | #87, #89 |

Branch protection and rulesets are GitHub settings, not effects of this YAML contract. Issue #89 must record the configured settings and the sole-maintainer review arrangement. Until settings are enforced, the owner follows the same checklist manually and reports the enforcement gap rather than describing an unprotected branch as protected.

### Exceptions and hotfixes

A hotfix starts from the currently deployed release commit on an issue-linked branch. It follows the same validation, PR, and evidence requirements, is merged into `main`, and is revalidated as a new candidate before deployment. If `main` contains other undeployed changes, qualify the complete candidate or hold promotion; do not bypass the candidate-source rule by silently deploying an arbitrary hotfix ref.

An exceptional administrative action requires a named owner, reason, affected control, approved scope, timestamp, compensating validation, and linked follow-up. Missing credentials, failed tests, unavailable reviewers for protected test/prod promotion, and absent environment rules do not turn into automatic approval. Do not weaken a gate to obtain a green run.

## 3. Promotion path across environments

The required portfolio path is **local development -> pull-request CI -> revalidated `main` candidate -> approved handoff -> local Docker Data-Lab `dev` verification -> release record**. Under #89's no-spend constraint, `test` and `prod` are protected, disabled policy definitions with no compute or cloud credentials. Snowflake remains a conceptual future target outside this portfolio implementation. Local Spark/Hive evidence does not qualify a Snowflake production deployment.

| Stage / GitHub environment | Execution target | Entry gate | Exit evidence and activation |
| --- | --- | --- | --- |
| Local development / none | Developer workspace and external Data-Lab; `local` profile where runtime execution is needed. | Issue-linked branch; local configuration stays private. | Local checks prepare the PR; this stage cannot publish a release. |
| PR CI / none | Ephemeral hosted runner; repository tests, contract checks, and offline dbt parse/docs. | `pull_request` targeting `main`; read-only token; no runtime credentials. | Applicable gates and summary succeed for the tested head/merge SHAs. Implement #85–#87. |
| Candidate validation / none | Hosted runner on the resulting `main` SHA. | Successful merge; revalidate that exact commit. | Candidate bundle, digests, reports, and evidence index. Implement #85, #88. |
| `dev` | Trusted, isolated Data-Lab runtime; Spark/Hive plus Airflow, artifact backend, metrics, and lineage services as configured. | Explicit dispatch by owner, verified candidate digest, configured environment rules, approved settings, and healthy runtime. | Success run, controlled failure/recovery, quality gates, artifact/log correlation, and metric/lineage checks. Enable through #88–#90. |
| `test` | Policy definition only; no runtime resources. | Disabled workflow path and branch allowlist, no self-review, no runtime credentials. | No deployment or warehouse qualification claimed. Future activation requires a separately reviewed design. |
| `prod` | Policy definition only; no runtime resources. | Disabled workflow path and branch allowlist, no self-review, no runtime credentials. | No production deployment claimed; no paid infrastructure required for local Phase 8 completion. |

### Runtime profiles are not GitHub environments

The [orchestration profiles](../airflow/config/orchestration_profiles.yml) are existing runtime configurations, not approval boundaries. The `ci` profile sets ingestion to dry-run but retains `dbt_build`, `dbt_test`, and a MongoDB artifact backend. Running that full DAG is not an offline hosted CI check. PR CI validates those configuration contracts and runs isolated tests; runtime DAG execution belongs in trusted `dev` verification with explicitly configured services. The `snowflake` profile is marked scaffold-only and must not be interpreted as a working deployment target.

GitHub environment names `dev`, `test`, and `prod` are configured allowlisted identifiers under #89; only `dev` has a handoff path. Before a handoff job starts, an unprivileged preflight verifies the selected environment exists, its approved protections are configured, the candidate belongs to `main`, artifact digests match, required validation succeeded, and requested target/profile configuration agrees. Fail closed if any prerequisite is missing; do not rely on implicit environment creation by the workflow.

### Approval, runner, and secret boundaries

- Keep validation, artifact packaging, and privileged deployment in separate jobs. Give each job only its necessary token permissions; PR CI has no environment association or deployment credentials.
- Use `workflow_dispatch` as the initial deployment trigger. Select an allowlisted environment and a full verified candidate SHA; reject arbitrary shell commands, feature refs, and unvalidated configuration overrides. Merging a PR or tagging a commit must not automatically deploy the runtime.
- Hosted runners produce a protected approval handoff; the owner explicitly consumes it using the local Docker operator. No self-hosted runner is registered and no public workflow reaches the persistent developer container.
- Store this portfolio's credentials only in the existing local Docker volume, in the private `0600` runtime JSON. No GitHub runtime secrets are required or uploaded. Keep non-sensitive paths and policy flags as environment variables. Do not commit secret values, upload private `.env` files, or put credentials in candidate bundles, command logs, or lineage facets.
- `dev` may use recorded owner approval for this single-maintainer portfolio; identify it as self-approval. `test` and `prod` require an independent authorized reviewer and no self-approval. They stay blocked if no such reviewer or protected target is available. No automated fallback bypasses this requirement.
- Apply environment branch/tag restrictions and serialize promotion per environment. Preserve the triggering actor, approver, source SHA, candidate digest, target/profile identity, and run/batch correlation keys in the deployment record.

### Runtime evidence and recovery acceptance

Dev promotion must demonstrate a successful pipeline path (`prepare -> ingestion -> transformation -> validation -> publish`) and preserve transformation order (`bronze -> silver -> gold -> kpi`). Run the established failure-blocking quality/governance checks and one deliberate failure followed by controlled recovery. A failed quality gate blocks release qualification even if downstream technical steps can run.

Archive sanitized summaries that correlate Airflow logs, artifact persistence, metric results, and OpenLineage/Marquez records. Treat an unreachable optional service as an explicitly accepted limitation only when its omission does not remove a required gate. Phase 7 manifest metadata and fixture metrics are useful smoke evidence, but do not replace a fresh runtime run for #90.

Record the prior verified candidate and compatible configuration before promotion. If verification fails, stop, capture the failure, and have the owner choose a compatible restore or forward fix. Database changes require separate migration/restore evidence. Repeat validation after recovery before publishing any release.

## 4. Milestone alignment and delivery handoff

### Dependency and priority order

| Issue | Priority / delivery step | Required deliverable | Dependency and exit evidence |
| --- | --- | --- | --- |
| #84 | P0 design foundation | This operating model and operational contract; four task commits. | Close after design review, link/contract validation, scoped graph refresh, and push. Does not close #83. |
| #85 | P0 CI foundation | PR and post-merge validation orchestration with a stable `CI Summary`. | Implements #84; prove a passing change and a failing mandatory check. |
| #86 | P0 dbt gates | Integrate the established parse, selectors, governance/contracts/failure-policy checks and docs generation. | Builds on #85; prove failures propagate to the aggregate check without a live warehouse. |
| #87 | P0 repository/Python gates | Clean-workspace Python tests and relevant standards/link/YAML checks. | Builds on #85; prove code and documentation changes receive the right checks. |
| #89 | P0 environment controls | Environment definitions, credentials/variables, review arrangement, branch/ref restrictions, and secret-safe execution. | Design alongside #88; configure and verify before any privileged live deployment. |
| #88 | P1 controlled deployment | Explicitly dispatched candidate verification and runtime adapter, with environment serialization and recovery handling. | May develop dry-run scaffolding alongside #89; live use requires #85–#87 and #89. |
| #90 | P1 end-to-end proof | Successful required `dev` path plus deliberate validation/promotion failure and controlled recovery. | Requires implemented #85–#89; archive real run/attempt IDs and sanitized evidence. |
| #91 | P1 final handoff | Reproducible operations/release runbook and consolidated Phase 8 outcome. | Use #90 evidence; state implemented controls and remaining limitations explicitly. |

Priority order follows control dependencies rather than issue-number order. No privileged deployment is enabled merely because #88 appears before #89 in the milestone.

### Relationship to completed and future phases

- Phases 0–5 supply standards, governed data contracts, deterministic generation, warehouse/dbt assets, and failure-blocking quality controls. CI reuses their existing validators rather than redefining domain semantics.
- Phase 6 supplies runtime topology, failure handling, artifacts, and the [CI/CD handoff checklist](airflow-orchestration-cicd-handoff-checklist.md). Hosted CI can prove repository contracts; actual DAG imports, success runs, and failure/recovery belong to the configured runtime verification path.
- Phase 7 supplies metrics, logs, lineage contracts, and [documented validation boundaries](phase-7-closeout.md). Preserve the distinction between fixture/manifest smoke evidence and fresh execution evidence.
- Phase 8 completes when #85–#91 provide repeatable validation, enforced merge/promotion controls, required local runtime evidence, and the final runbook. A conditional cloud path must be described as disabled or qualified for a named target; it cannot be represented as production validation by inference.
- Phase 9 analytics consumes a known, traceable code/data-model baseline with the CI gates available for subsequent dashboard/model changes. Phase 10 completes operational hardening and final reproducibility. These later milestones are not automatically completed by a passing Phase 8 workflow.

### Issue #84 acceptance and owner decisions

The four issue tasks are satisfied by sections 1–4 and the matching sections of the operational contract. Owner: `Shreyash2942`. The agreed defaults are issue-linked phase branches, merge commits preserving task history, recorded sole-maintainer acceptance for the portfolio, explicit `dev` promotion, and disabled cloud promotion until independent approval and target prerequisites exist.

Review the design against the following scenarios before implementation:

| Scenario | Required decision |
| --- | --- |
| Documentation-only PR | Run standards validation and `CI Summary`; record why runtime jobs are inapplicable. |
| Python/dbt/contract change | Run affected validators and require every applicable result in the summary. |
| Untrusted fork PR | Use hosted isolated validation without deployment secrets or persistent self-hosted execution. |
| PR passed but merged SHA differs | Revalidate the actual `main` commit before packaging a candidate. |
| Candidate digest or material configuration changes | Reject old qualification and repeat affected validation. |
| Unknown/unprotected environment or unavailable required approval | Stop before privileged execution. |
| Current scaffold-only Snowflake profile selected | Reject live cloud promotion until its activation prerequisites are proved. |
| Runtime quality gate fails | Stop promotion, retain failure evidence, and perform a documented recovery decision. |
| Issue #84 design is closed | Leave #83 and #85–#91 open; continue implementation on the Phase 8 branch. |

These are reviewed design outcomes. Executable demonstration and enforcement are acceptance work for #85–#90. No live GitHub settings, deployment workflow, release tag, credentials, or runtime resource is created by issue #84.

### Source references

The design follows GitHub's documented [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), and [secure workflow practices](https://docs.github.com/en/actions/reference/security/secure-use). Workflow and repository-setting implementation is tracked separately from this design.
