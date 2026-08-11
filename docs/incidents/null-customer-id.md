# Incident Report: NULL customer_id

## 1. Incident
- **ID**: `inc_null_customer_001`
- **Severity**: HIGH
- **Affected Assets**: `stg_orders`, `fct_orders`, `dim_customers`

## 2. Trigger
- **Command**: `python -m failure_injection.runner --scenario null_customer_id`
- **Mechanism**: Ingestion step injects `NULL` values into the `customer_id` attribute of incoming batch order records.

## 3. Signals
- `SignalType.DBT_TEST_FAILURE` (Severity: HIGH)
- **Test Name**: `not_null_stg_orders_customer_id`
- **Asset**: `stg_orders`

## 4. Evidence
- dbt data test `not_null_stg_orders_customer_id` failed with 2 result rows.
- Raw payload in `raw_data.orders` contains unpopulated customer keys.
- Ingestion pipeline step completed without schema parsing errors, but downstream data quality assertion caught unpopulated keys.

## 5. Root Cause
Upstream source data-quality regression introduced `NULL` `customer_id` values into the batch order payload prior to ingestion.

## 6. Impact
Downstream order analytics, customer lifetime value calculations, and dimensional models (`dim_customers`) will contain unassigned customer revenue.

## 7. Recommended Remediation
1. Quarantine affected records containing `NULL` `customer_id`.
2. Validate upstream source API extraction payload.
3. Re-execute dbt model transformations after source data correction.

## 8. Expected System Behavior
- The pipeline execution halts at the dbt test phase.
- Dagster records `dbt_test_results` asset failure.
- Diagnosis Engine detects rule match (`NullKeyRule`) with **95% confidence**.
- Platform produces a structured incident report and awaits human remediation approval.
