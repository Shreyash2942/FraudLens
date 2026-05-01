# Phase 3 Config

This folder stores non-secret runtime profiles for Phase 3 setup.

## Files

- `local.yml`: local-first profile for container-based testing
- `cloud.yml`: cloud-ready profile for Snowflake execution
- `env.example`: required environment variable contract (copy values locally, do not commit secrets)

## Usage

- select profile with `PHASE3_ENV` (`local` or `cloud`)
- run `../scripts/print_runtime_config.py` to verify resolved settings
- keep credentials in local env files or secret manager, not in YAML
