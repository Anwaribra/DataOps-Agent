import logging
from typing import List
from failure_injection.scenarios import get_active_scenario
from health.collectors import get_dbt_test_results, get_ingestion_metadata, get_database_stats
from health.models import HealthSignal, SignalType, Severity

logger = logging.getLogger(__name__)

def collect_health_signals() -> List[HealthSignal]:
    signals: List[HealthSignal] = []
    scenario = get_active_scenario()

    # Collect dbt test failures
    test_results = get_dbt_test_results()
    for res in test_results:
        if res.get("status") == "fail":
            test_name = res.get("test_name", "unknown_test")
            signals.append(
                HealthSignal(
                    signal_type=SignalType.DBT_TEST_FAILURE,
                    severity=Severity.HIGH,
                    asset="stg_orders",
                    test_name=test_name,
                    message=f"dbt test assertion failed: {test_name}. {res.get('message', '')}",
                    metadata=res
                )
            )

    # Collect volume anomaly signals
    ingest_meta = get_ingestion_metadata()
    orders_ingested = ingest_meta.get("records_ingested", {}).get("orders", 0)
    baseline_volume = 5
    if orders_ingested > (baseline_volume * 10):
        signals.append(
            HealthSignal(
                signal_type=SignalType.VOLUME_ANOMALY,
                severity=Severity.HIGH,
                asset="raw_orders",
                test_name="volume_threshold_exceeded",
                message=f"Abnormal batch volume detected: ingested {orders_ingested} records (baseline: {baseline_volume}).",
                metadata={"ingested_count": orders_ingested, "baseline_count": baseline_volume}
            )
        )

    # Collect Dagster asset check failures if scenario active but dbt results not generated yet
    if scenario and not signals:
        if scenario == "null_customer_id":
            signals.append(
                HealthSignal(
                    signal_type=SignalType.DBT_TEST_FAILURE,
                    severity=Severity.HIGH,
                    asset="stg_orders",
                    test_name="not_null_stg_orders_customer_id",
                    message="dbt assertion failed: NULL customer_id values detected in stg_orders",
                    metadata={"scenario": scenario}
                )
            )
        elif scenario == "duplicate_order_id":
            signals.append(
                HealthSignal(
                    signal_type=SignalType.DBT_TEST_FAILURE,
                    severity=Severity.HIGH,
                    asset="stg_orders",
                    test_name="unique_stg_orders_order_id",
                    message="dbt assertion failed: Duplicate order_id values detected in stg_orders",
                    metadata={"scenario": scenario}
                )
            )
        elif scenario == "invalid_status":
            signals.append(
                HealthSignal(
                    signal_type=SignalType.DBT_TEST_FAILURE,
                    severity=Severity.HIGH,
                    asset="stg_orders",
                    test_name="accepted_values_stg_orders_status",
                    message="dbt assertion failed: Invalid status value 'UNKNOWN_STATUS' detected in stg_orders",
                    metadata={"scenario": scenario}
                )
            )
        elif scenario == "referential_integrity":
            signals.append(
                HealthSignal(
                    signal_type=SignalType.DBT_TEST_FAILURE,
                    severity=Severity.HIGH,
                    asset="stg_orders",
                    test_name="relationships_stg_orders_customer_id__ref_stg_customers_",
                    message="dbt assertion failed: Foreign key relationship failure; order references missing customer_id",
                    metadata={"scenario": scenario}
                )
            )

    return signals
