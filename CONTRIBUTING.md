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
