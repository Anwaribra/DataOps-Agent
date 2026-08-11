import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from failure_injection.scenarios import get_active_scenario
from health.models import HealthSignal, SignalType, Severity

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DBT_TARGET_DIR = BASE_DIR / "dbt" / "target"

# Static lineage map for e-commerce pipeline
ASSET_LINEAGE = {
    "raw_customers": [],
    "raw_products": [],
    "raw_orders": [],
    "raw_payments": [],
    "stg_customers": ["raw_customers"],
    "stg_products": ["raw_products"],
    "stg_orders": ["raw_orders"],
    "stg_payments": ["raw_payments"],
    "int_customer_orders": ["stg_orders", "stg_payments"],
    "fct_orders": ["stg_orders", "stg_payments"],
    "dim_customers": ["stg_customers", "int_customer_orders"],
    "dim_products": ["stg_products"]
}


def get_failed_assets() -> List[str]:
    scenario = get_active_scenario()
    failed = []
    if scenario in ("null_customer_id", "duplicate_order_id", "invalid_status", "referential_integrity"):
        failed.extend(["stg_orders", "fct_orders"])
    elif scenario == "volume_anomaly":
        failed.append("stg_orders")
    return list(set(failed))


def get_asset_lineage(asset_name: str) -> Dict[str, Any]:
    upstream = ASSET_LINEAGE.get(asset_name, [])
    downstream = [a for a, deps in ASSET_LINEAGE.items() if asset_name in deps]
    return {
        "asset": asset_name,
        "upstream": upstream,
        "downstream": downstream
    }


def get_recent_runs(asset_name: str) -> List[Dict[str, Any]]:
    scenario = get_active_scenario()
    status = "failed" if asset_name in get_failed_assets() else "success"
    return [
        {
            "run_id": "run_latest_001",
            "asset": asset_name,
            "status": status,
            "timestamp": "2026-02-25T12:00:00Z"
        },
        {
            "run_id": "run_prev_000",
            "asset": asset_name,
            "status": "success",
            "timestamp": "2026-02-24T12:00:00Z"
        }
    ]


def get_dbt_test_results() -> List[Dict[str, Any]]:
    scenario = get_active_scenario()
    if scenario == "null_customer_id":
        return [{
            "test_name": "not_null_stg_orders_customer_id",
            "status": "fail",
            "failures": 2,
            "message": "Got 2 results, configured to fail if != 0"
        }]
    elif scenario == "duplicate_order_id":
        return [{
            "test_name": "unique_stg_orders_order_id",
            "status": "fail",
            "failures": 1,
            "message": "Got 1 result, configured to fail if != 0"
        }]
    elif scenario == "invalid_status":
        return [{
            "test_name": "accepted_values_stg_orders_status",
            "status": "fail",
            "failures": 1,
            "message": "Got 1 result: 'UNKNOWN_STATUS'"
        }]
    elif scenario == "referential_integrity":
        return [{
            "test_name": "relationships_stg_orders_customer_id__ref_stg_customers_",
            "status": "fail",
            "failures": 1,
            "message": "Found 1 order referencing non-existent customer_id 'cust_non_existent_999'"
        }]

    results_file = DBT_TARGET_DIR / "run_results.json"
    if results_file.exists():
        try:
            with open(results_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                tests = []
                for res in data.get("results", []):
                    if res.get("unique_id", "").startswith("test."):
                        tests.append({
                            "test_name": res.get("unique_id"),
                            "status": res.get("status"),
                            "failures": res.get("failures", 0),
                            "execution_time": res.get("execution_time", 0)
                        })
                return tests
        except Exception as e:
            logger.warning(f"Could not parse dbt run_results.json: {e}")

    return []


def get_ingestion_metadata() -> Dict[str, Any]:
    scenario = get_active_scenario()
    record_count = 505 if scenario == "volume_anomaly" else 5
    return {
        "pipeline": "ecommerce_ingestion",
        "active_scenario": scenario or "healthy",
        "last_ingestion_timestamp": "2026-02-25T12:00:00Z",
        "records_ingested": {
            "customers": 5,
            "products": 5,
            "orders": record_count,
            "payments": 5
        }
    }


def get_database_stats() -> Dict[str, Any]:
    scenario = get_active_scenario()
    orders_count = 505 if scenario == "volume_anomaly" else (6 if scenario in ("duplicate_order_id", "invalid_status", "referential_integrity") else 5)
    null_customer_count = 2 if scenario == "null_customer_id" else 0
    return {
        "schemas": ["raw_data", "staging", "intermediate", "marts"],
        "tables": {
            "raw_data.orders": {"rows": orders_count, "null_customer_id_rows": null_customer_count},
            "marts.fct_orders": {"rows": orders_count if scenario != "null_customer_id" else 3}
        }
    }
