import pytest
from failure_injection.scenarios import set_active_scenario
from health.aggregator import collect_health_signals
from health.collectors import (
    get_failed_assets,
    get_asset_lineage,
    get_recent_runs,
    get_ingestion_metadata,
    get_database_stats
)
from health.models import HealthSignal, SignalType, Severity

def test_health_signal_model_creation():
    sig = HealthSignal(
        signal_type=SignalType.DBT_TEST_FAILURE,
        severity=Severity.HIGH,
        asset="stg_orders",
        test_name="not_null_stg_orders_customer_id",
        message="NULL customer_id failure"
    )
    assert sig.signal_id.startswith("sig_")
    assert sig.severity == Severity.HIGH
    assert sig.asset == "stg_orders"

def test_collectors_data_retrieval():
    lineage = get_asset_lineage("stg_orders")
    assert lineage["asset"] == "stg_orders"
    assert "raw_orders" in lineage["upstream"]

    runs = get_recent_runs("stg_orders")
    assert len(runs) >= 1

    ingest_meta = get_ingestion_metadata()
    assert "records_ingested" in ingest_meta

    db_stats = get_database_stats()
    assert "schemas" in db_stats

def test_aggregator_signal_collection():
    set_active_scenario("null_customer_id")
    signals = collect_health_signals()
    assert len(signals) >= 1
    sig = signals[0]
    assert sig.signal_type == SignalType.DBT_TEST_FAILURE
    assert "not_null" in sig.test_name
    set_active_scenario(None)
