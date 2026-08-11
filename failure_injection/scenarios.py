import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "data" / "sample"
STATE_FILE = Path(__file__).resolve().parent / "active_scenario.json"

SCENARIOS = {
    "null_customer_id": {
        "description": "Inject NULL customer_id into order records",
        "expected_failure": "dbt not_null test failure on customer_id"
    },
    "duplicate_order_id": {
        "description": "Inject duplicate order_id records",
        "expected_failure": "dbt unique test failure on order_id"
    },
    "invalid_status": {
        "description": "Inject unsupported order status ('UNKNOWN_STATUS')",
        "expected_failure": "dbt accepted_values test failure on status"
    },
    "referential_integrity": {
        "description": "Inject order referencing a non-existent customer ('cust_non_existent_999')",
        "expected_failure": "dbt relationships test failure"
    },
    "volume_anomaly": {
        "description": "Inject abnormal volume of order records (500+ records)",
        "expected_failure": "Volume anomaly health signal detection"
    }
}


def set_active_scenario(scenario_name: Optional[str]) -> Dict[str, Any]:
    if scenario_name and scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: '{scenario_name}'. Available: {list(SCENARIOS.keys())}")
    
    state = {
        "active_scenario": scenario_name,
        "scenario_info": SCENARIOS.get(scenario_name) if scenario_name else None
    }
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    
    if scenario_name:
        logger.info(f"Activated failure scenario: {scenario_name}")
    else:
        logger.info("Reset failure scenarios. Pipeline returned to HEALTHY state.")
    return state


def get_active_scenario() -> Optional[str]:
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("active_scenario")
    except Exception:
        return None


def apply_scenario_transformations(resource_name: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scenario = get_active_scenario()
    if not scenario:
        return records

    records_copy = [dict(r) for r in records]

    if scenario == "null_customer_id" and resource_name == "orders":
        logger.warning("[Failure Injection] Applying 'null_customer_id' scenario to orders.")
        if records_copy:
            records_copy[0]["customer_id"] = None
            if len(records_copy) > 1:
                records_copy[1]["customer_id"] = None

    elif scenario == "duplicate_order_id" and resource_name == "orders":
        logger.warning("[Failure Injection] Applying 'duplicate_order_id' scenario to orders.")
        if records_copy:
            dup = records_copy[0].copy()
            dup["order_date"] = "2026-02-22T10:00:00Z"
            records_copy.append(dup)

    elif scenario == "invalid_status" and resource_name == "orders":
        logger.warning("[Failure Injection] Applying 'invalid_status' scenario to orders.")
        if records_copy:
            corrupted = records_copy[0].copy()
            corrupted["order_id"] = "ord_status_err_999"
            corrupted["status"] = "UNKNOWN_STATUS"
            records_copy.append(corrupted)

    elif scenario == "referential_integrity" and resource_name == "orders":
        logger.warning("[Failure Injection] Applying 'referential_integrity' scenario to orders.")
        if records_copy:
            orphan = records_copy[0].copy()
            orphan["order_id"] = "ord_orphan_888"
            orphan["customer_id"] = "cust_non_existent_999"
            records_copy.append(orphan)

    elif scenario == "volume_anomaly" and resource_name == "orders":
        logger.warning("[Failure Injection] Applying 'volume_anomaly' scenario to orders.")
        base_record = records_copy[0] if records_copy else {"order_id": "ord_vol_0", "customer_id": "cust_101", "status": "completed", "total_amount": 10.0}
        for i in range(1, 501):
            records_copy.append({
                "order_id": f"ord_vol_batch_{i}",
                "customer_id": "cust_101",
                "order_date": "2026-02-25T12:00:00Z",
                "status": "completed",
                "total_amount": 25.0,
                "payment_method": "credit_card"
            })

    return records_copy
