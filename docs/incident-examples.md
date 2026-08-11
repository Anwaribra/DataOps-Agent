# Incident Diagnosis Scenarios & Failure Injection

This document outlines potential failure scenarios that can be injected into the DataOps Agent platform and diagnosed by the agent.

## Scenario 1: Duplicate Order IDs

### Cause
The upstream ingestion source emits a duplicated order record with `order_id = "ord_301"`.

### Failure Trigger
```bash
python -m ingestion.pipeline --inject-duplicate-orders
```

### Data Quality Test Triggered
- dbt test `unique_stg_orders_order_id` FAILS in staging layer.
- Dagster `dbt_test_results` asset fails execution.

### Agent Diagnosis (Phase 2)
1. Agent queries dbt test logs via MCP tool `get_dbt_test_failures()`.
2. Agent traces lineage back to `raw_data.orders` table in PostgreSQL.
3. Agent identifies duplicate `order_id` values ingested during batch run.
4. Agent proposes deduplication or filtering remediation for human approval.

---

## Scenario 2: Null Customer ID (Orphan Orders / Missing FK)

### Cause
An upstream source emits a customer record missing a primary key `customer_id = None`.

### Failure Trigger
```bash
python -m ingestion.pipeline --inject-null-customer
```

### Data Quality Test Triggered
- dbt test `not_null_stg_customers_customer_id` FAILS.
- dbt test `relationships_stg_orders_customer_id__customer_id__ref_stg_customers_` FAILS.

### Agent Diagnosis (Phase 2)
1. Agent detects broken relationship test between `stg_orders` and `stg_customers`.
2. Agent inspects `stg_customers` raw table using `execute_read_only_query()`.
3. Agent pinpoints null key corruption in customer batch file.
4. Agent requests operator permission to isolate corrupted customer record.

---

## Scenario 3: Invalid Order Status Enum

### Cause
An order record is submitted with an unhandled status string (e.g. `"INVALID_STATUS_UNKNOWN"`).

### Failure Trigger
```bash
python -m ingestion.pipeline --inject-invalid-status
```

### Data Quality Test Triggered
- dbt test `accepted_values_stg_orders_status__completed__pending__shipped__cancelled__refunded` FAILS.

### Agent Diagnosis (Phase 2)
1. Agent checks failed test output.
2. Identifies unexpected value `"INVALID_STATUS_UNKNOWN"` in order record `ord_corrupted_999`.
3. Recommends enum mapping update or record quarantine.
