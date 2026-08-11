# Incident Report: Invalid Order Status

## 1. Incident
- **ID**: `inc_invalid_status_003`
- **Severity**: HIGH
- **Affected Assets**: `stg_orders`, `fct_orders`

## 2. Trigger
- **Command**: `python -m failure_injection.runner --scenario invalid_status`
- **Mechanism**: Ingestion payload contains unhandled order status value `"UNKNOWN_STATUS"`.

## 3. Signals
- `SignalType.DBT_TEST_FAILURE` (Severity: HIGH)
- **Test Name**: `accepted_values_stg_orders_status`
- **Asset**: `stg_orders`

## 4. Evidence
- dbt accepted_values test failed on `stg_orders.status`.
- Allowed enum values: `['completed', 'pending', 'shipped', 'cancelled', 'refunded']`.
- Observed invalid value: `'UNKNOWN_STATUS'`.

## 5. Root Cause
Upstream order management system emitted unhandled order status string `"UNKNOWN_STATUS"` into batch payload.

## 6. Impact
Order status filtering, state machine transitions, and revenue analytics will fail to categorize invalid orders.

## 7. Recommended Remediation
1. Update status mapping logic in `stg_orders.sql` or sanitize upstream enum values.
2. Quarantine invalid status records into exception table.
3. Re-run dbt data quality suite.

## 8. Expected System Behavior
- Accepted values assertion fails.
- Diagnosis Engine matches `InvalidStatusRule` with **90% confidence**.
- Platform proposes enum mapping or record quarantine action.
