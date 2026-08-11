# Failure Injection Framework

The Failure Injection Framework enables deterministic, reversible, and isolated testing of pipeline resilience, health signal detection, and automated error diagnosis.

## Supported Scenarios

| Scenario Name | Target Entity | Mechanism | Expected Platform Result |
|---|---|---|---|
| `null_customer_id` | `orders` | Injects `NULL` values into `customer_id` | dbt `not_null` test failure on `customer_id` |
| `duplicate_order_id` | `orders` | Injects duplicate `order_id` record | dbt `unique` test failure on `order_id` |
| `invalid_status` | `orders` | Injects unsupported status string (`"UNKNOWN_STATUS"`) | dbt `accepted_values` test failure on `status` |
| `referential_integrity` | `orders` | References non-existent customer (`"cust_non_existent_999"`) | dbt `relationships` test failure |
| `volume_anomaly` | `orders` | Injects 500+ order records into single batch | Volume anomaly signal detection |

## Usage Commands

### List Scenarios
```bash
python -m failure_injection.runner --list
```

### Activate a Scenario
```bash
python -m failure_injection.runner --scenario null_customer_id
```

### Check Active Scenario Status
```bash
python -m failure_injection.runner --status
```

### Reset to Healthy Pipeline State
```bash
python -m failure_injection.runner --reset
```
