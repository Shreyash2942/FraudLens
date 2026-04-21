# Platform

This directory defines the Phase 1 integration contract between FraudLens and the external runtime project at `https://github.com/Shreyash2942/Data-Lab.git`.

## Files

- `service-inventory.yaml` expected platform services, endpoints, auth modes, and FraudLens dependencies
- `connectivity-matrix.md` mapping between FraudLens subsystems and runtime services
- `local-setup.md` local integration notes for developers using the external runtime

## Phase 1 Position

- FraudLens does not duplicate the Docker stack here.
- Data-Lab remains the runtime source.
- FraudLens captures the service contract, validation expectations, and local configuration shape needed by later phases.
- The contract is capability-based, not container-count-based.
- One all-in-one local container is acceptable if it exposes or documents the capabilities FraudLens needs.
