# Local Setup Notes

## Runtime Source

FraudLens Phase 1 depends on the external runtime repository:

- `https://github.com/Shreyash2942/Data-Lab.git`

Do not recreate that stack inside FraudLens in this phase.

## Local Developer Flow

1. Clone or update the external Data-Lab repository.
2. Follow the upstream runtime instructions from the Data-Lab README to start the local environment.
3. In FraudLens, copy `.env.example` to `.env`.
4. Replace placeholder values locally without committing secrets.
5. Use `documents/platform-validation-runbook.md` to validate that the runtime satisfies the FraudLens platform contract.

## FraudLens Configuration Intent

FraudLens stores only integration-facing values such as:

- service base URLs
- bucket names
- host and port values
- usernames and passwords as local-only placeholders

FraudLens does not store live runtime secrets or operating credentials in source control.

## Snowflake Versus Local Sandbox

- Snowflake remains the target analytical platform for the project
- Data-Lab is the local all-in-one development sandbox
- Spark and Hive can be used locally to replicate selected warehouse patterns and reduce cloud spend
- use the Snowflake account only for the parts of the project that need real platform validation

## Local Override Guidance

- If Data-Lab exposes different ports on your machine, update your local `.env`.
- If a required FraudLens service is not yet exposed by Data-Lab, document the gap in the related Phase 1 issue instead of inventing an undocumented workaround in this repo.
- Keep runtime-specific adjustments local unless they represent a durable platform contract change that should be documented for the team.
