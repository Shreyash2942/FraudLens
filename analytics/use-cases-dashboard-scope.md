# Analytics use cases and dashboard scope

Issue [#93](https://github.com/Shreyash2942/FraudLens/issues/93), parent [#92](https://github.com/Shreyash2942/FraudLens/issues/92), Phase 9: Analytics & Dashboard. Design date: November 25, 2026 (America/New_York).

## Audiences and decisions

| Audience | Decisions to support | Planned dashboard | Expected use |
| --- | --- | --- | --- |
| Executive / fraud strategy sponsor | Recognize changes in transaction and alert activity; direct attention to high-severity exposure and portfolio risk posture. | Executive KPI (#95) | Read-only daily trend review and portfolio demo; distinguish daily activity from a build-wide snapshot. |
| Fraud operations lead | Understand alert severity/status/queue and owning-team distribution; prioritize investigation of operational patterns. | Fraud Operations (#96) | Read-only operational review and alert-to-case context; not an action queue or case-management application. |
| Fraud / payments analyst | Compare channel and transaction-status mix, reversal/cross-border patterns and supporting payment context. | Transaction & Channel Analysis (#97) | Filtered exploration and governed identifier drill-through; reconcile observations to Gold rows. |

All audiences consume the same governed Gold definitions. These are proposed portfolio personas, not claims of stakeholder interviews or production user acceptance. Named operational owners and acceptance evidence are established during dashboard review.

Each page must explain its audience, date meaning, grain, active filters, source/build provenance and limitations. A visibly synthetic-data label is mandatory. Use masked/minimal identifiers in demo exports; never expose service credentials or banking-like detail merely because a source field exists.
