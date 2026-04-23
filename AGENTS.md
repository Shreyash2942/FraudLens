## FraudLens Context

FraudLens is a standards-first banking fraud analytics portfolio project.

Current project position:
- Phase 0 established the repo foundation, standards, governed specs, and GitHub workflow scaffolding.
- Phase 1 documents the external platform contract and treats `Shreyash2942/Data-Lab` as the local runtime sandbox.
- Phase 2 implements the synthetic data foundation with deterministic generation, validation, curated blueprints, and optional MinIO upload.

Key architectural facts:
- Snowflake is the target analytics platform.
- Spark and Hive are local cost-saving surrogates for development and testing.
- The synthetic generator lives in `synthetic_generator/`.
- Generated local data lands under `data/batches/<batch_id>/`.
- The current governed model includes 21 generated datasets:
  core banking/fraud datasets plus calendar, geography, and organization dimensions for dashboard control.

Important modeling direction:
- ISO 20022-inspired semantics for payments/accounts/transactions
- BIAN-inspired business-domain grouping
- custom fraud operations entities for risk, alerts, cases, investigations, decisions, and dispositions
- org/dashboard dimensions for region, branch territory, business unit, analyst team, and calendar

## graphify

This project has a local graphify knowledge graph at `graphify-out/`.

Rules:
- Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files first.
- After modifying code files in this session, run `py -m graphify update .` to refresh the code graph.
- If major docs/specs change, rebuild or refresh the graph so the project memory stays aligned with the repo state.
