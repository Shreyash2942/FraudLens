# Governance Controls

## Control Objectives

- preserve traceability of critical business definitions
- require approval for changes to governed contracts
- maintain accountability for business and technical stewardship
- prevent unmanaged changes to KPI-driving entities

## Control Categories

### Ownership

- every critical contract must identify a business owner
- every critical contract must identify a technical steward

### Approval

- changes to critical contracts require explicit review before merge
- approval expectations should be described in the contract metadata

### Traceability

- every change should be linked to an issue
- PRs should explain the control impact of the change
- relationship changes must be documented in `specs/relationship-map.yaml`

### Segregation

- no contract should assume the same persona both raises and adjudicates fraud without an auditable handoff
- case, decision, and disposition objects should stay distinct for later operational controls

## Critical Dataset Expectations

At minimum, the following should be treated as critical:

- payment instructions
- payment transactions
- deposit accounts
- fraud alerts
- fraud cases
- decision records
- case dispositions
