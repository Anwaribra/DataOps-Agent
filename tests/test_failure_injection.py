import pytest
from failure_injection.scenarios import (
    SCENARIOS,
    set_active_scenario,
    get_active_scenario,
    apply_scenario_transformations
)

def test_all_scenarios_exist():
    expected = ["null_customer_id", "duplicate_order_id", "invalid_status", "referential_integrity", "volume_anomaly"]
    for sc in expected:
        assert sc in SCENARIOS

def test_set_and_reset_scenario():
    set_active_scenario("null_customer_id")
    assert get_active_scenario() == "null_customer_id"

    set_active_scenario(None)
    assert get_active_scenario() is None

def test_null_customer_id_transformation():
    set_active_scenario("null_customer_id")
    orders = [{"order_id": "ord_1", "customer_id": "cust_101"}]
    transformed = apply_scenario_transformations("orders", orders)
    assert transformed[0]["customer_id"] is None
    set_active_scenario(None)

def test_duplicate_order_id_transformation():
    set_active_scenario("duplicate_order_id")
    orders = [{"order_id": "ord_1", "customer_id": "cust_101"}]
    transformed = apply_scenario_transformations("orders", orders)
    assert len(transformed) == 2
    assert transformed[0]["order_id"] == transformed[1]["order_id"]
    set_active_scenario(None)

def test_invalid_status_transformation():
    set_active_scenario("invalid_status")
    orders = [{"order_id": "ord_1", "customer_id": "cust_101"}]
    transformed = apply_scenario_transformations("orders", orders)
    assert len(transformed) == 2
    assert transformed[1]["status"] == "UNKNOWN_STATUS"
    set_active_scenario(None)

def test_referential_integrity_transformation():
    set_active_scenario("referential_integrity")
    orders = [{"order_id": "ord_1", "customer_id": "cust_101"}]
    transformed = apply_scenario_transformations("orders", orders)
    assert len(transformed) == 2
    assert transformed[1]["customer_id"] == "cust_non_existent_999"
    set_active_scenario(None)

def test_volume_anomaly_transformation():
    set_active_scenario("volume_anomaly")
    orders = [{"order_id": "ord_1", "customer_id": "cust_101"}]
    transformed = apply_scenario_transformations("orders", orders)
    assert len(transformed) > 500
    set_active_scenario(None)
