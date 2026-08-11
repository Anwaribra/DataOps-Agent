# Incident Report: Duplicate order_id

## 1. Incident
- **ID**: `inc_duplicate_order_002`
- **Severity**: HIGH
- **Affected Assets**: `stg_orders`, `fct_orders`

## 2. Trigger
- **Command**: `python -m failure_injection.runner --scenario duplicate_order_id`
- **Mechanism**: Upstream batch emits duplicate order record (`order_id = "ord_301"`).

## 3. Signals
- `SignalType.DBT_TEST_FAILURE` (Severity: HIGH)
- **Test Name**: `unique_stg_orders_order_id`
- **Asset**: `stg_orders`

## 4. Evidence
- dbt data test `unique_stg_orders_order_id` failed.
- Primary key uniqueness constraint violated on `stg_orders.order_id`.
- Multiple rows sharing identical `order_id` found in `raw_data.orders`.

## 5. Root Cause
Upstream batch ingestion produced duplicate `order_id` records in the source dataset due to ingestion payload replay.

## 6. Impact
Revenue fact tables (`fct_orders`) and daily sales aggregates will double-count transaction totals.

## 7. Recommended Remediation
1. Deduplicate records in `raw_data.orders` using window functions (`ROW_NUMBER()`).
2. Audit upstream `dlt` write disposition settings (`replace` vs `append`).
3. Re-run dbt staging and mart models.

## 8. Expected System Behavior
- dbt test phase flags uniqueness failure.
- Diagnosis Engine matches `DuplicateOrderRule` with **92% confidence**.
- Platform isolates duplicate primary keys and generates remediation instructions.
