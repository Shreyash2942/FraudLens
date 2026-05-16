# Gold Dimension Models

Issue `#52` implements conformed Gold dimensions for consistent analytics slicing and filtering.

## Implemented Dimensions

- `dim_customer` (`GOLD_DIM_CUSTOMER`)
- `dim_account` (`GOLD_DIM_ACCOUNT`)
- `dim_card` (`GOLD_DIM_CARD`)
- `dim_merchant` (`GOLD_DIM_MERCHANT`)
- `dim_branch` (`GOLD_DIM_BRANCH`)
- `dim_device` (`GOLD_DIM_DEVICE`)
- `dim_date` (`GOLD_DIM_DATE`)
- supporting lookup dimensions:
  - `dim_region` (`GOLD_DIM_REGION`)
  - `dim_business_unit` (`GOLD_DIM_BUSINESS_UNIT`)
  - `dim_analyst_team` (`GOLD_DIM_ANALYST_TEAM`)
  - `dim_channel` (`GOLD_DIM_CHANNEL`)
  - `dim_reference_code` (`GOLD_DIM_REFERENCE_CODE`)
  - `dim_customer_org_assignment` (`GOLD_DIM_CUSTOMER_ORG_ASSIGNMENT`)

## Design Notes

- all dimensions source from conformed Silver models only
- hierarchy handling:
  - branch rolls up through territory to region
  - organization dimensions preserve business unit and analyst team context
- SCD-style handling:
  - customer organizational assignments are modeled in `dim_customer_org_assignment`
  - current assignment projection is exposed directly in `dim_customer`

## Validation Assets

- schema tests: `dbt/models/gold/dimensions/gold_dimension_models.yml`
- singular test: `dbt/tests/gold/test_dim_customer_org_assignment_no_overlap.sql`
