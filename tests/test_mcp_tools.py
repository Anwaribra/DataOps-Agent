import pytest
from failure_injection.scenarios import set_active_scenario
from mcp.tools.dagster import (
    get_failed_assets_tool,
    get_asset_status_tool,
    get_asset_lineage_tool,
    get_recent_runs_tool,
    get_asset_checks_tool
)
from mcp.tools.dbt import (
    get_dbt_test_results_tool,
    get_dbt_model_status_tool,
    get_failed_dbt_tests_tool
)
from mcp.tools.incidents import (
    list_incidents_tool,
    get_incident_tool,
    get_incident_evidence_tool,
    get_diagnosis_tool
)
from mcp.tools.database import (
    get_table_stats_tool,
    get_column_stats_tool,
    get_recent_data_quality_stats_tool
)
from mcp.tools.ingestion import (
    get_ingestion_status_tool,
    get_ingestion_metadata_tool
)

def test_dagster_tools():
    set_active_scenario("null_customer_id")
    failed = get_failed_assets_tool()
    assert "assets" in failed
    assert len(failed["assets"]) > 0

    status = get_asset_status_tool("stg_orders")
    assert status["asset_name"] == "stg_orders"
    assert status["status"] == "FAILED"

    lineage = get_asset_lineage_tool("stg_orders")
    assert lineage["asset"] == "stg_orders"
    assert "raw_orders" in lineage["upstream"]

    runs = get_recent_runs_tool("stg_orders", limit=3)
    assert len(runs["runs"]) <= 3

    checks = get_asset_checks_tool("stg_orders")
    assert len(checks["checks"]) > 0
    set_active_scenario(None)

def test_dbt_tools():
    set_active_scenario("duplicate_order_id")
    all_tests = get_dbt_test_results_tool()
    assert "tests" in all_tests

    model_status = get_dbt_model_status_tool("stg_orders")
    assert model_status["model_name"] == "stg_orders"
    assert model_status["materialization"] == "view"

    failed_tests = get_failed_dbt_tests_tool()
    assert "failed_tests" in failed_tests
    assert len(failed_tests["failed_tests"]) > 0
    set_active_scenario(None)

def test_incident_tools():
    set_active_scenario("null_customer_id")
    incidents = list_incidents_tool()
    assert len(incidents["incidents"]) > 0

    inc_id = incidents["incidents"][0]["incident_id"]
    inc_detail = get_incident_tool(inc_id)
    assert "incident" in inc_detail

    evidence = get_incident_evidence_tool(inc_id)
    assert len(evidence["evidence"]) > 0

    diagnosis = get_diagnosis_tool(inc_id)
    assert diagnosis["confidence"] > 0.0
    set_active_scenario(None)

def test_database_tools_allowed_table():
    stats = get_table_stats_tool("staging.stg_orders")
    assert stats["is_allowed"] is True
    assert stats["table_name"] == "staging.stg_orders"

    col_stats = get_column_stats_tool("staging.stg_orders", "order_id")
    assert col_stats["column_name"] == "order_id"

    quality = get_recent_data_quality_stats_tool("staging.stg_orders")
    assert "quality_score" in quality

def test_database_tools_security_rejection():
    # Attempting to access an unapproved table should return structured error
    res = get_table_stats_tool("pg_catalog.pg_user")
    assert "error" in res
    assert "Access denied" in res["error"]

def test_ingestion_tools():
    status = get_ingestion_status_tool()
    assert status["pipeline_name"] == "ecommerce_ingestion"

    meta = get_ingestion_metadata_tool()
    assert "records_ingested" in meta
