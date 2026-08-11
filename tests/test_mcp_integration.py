import pytest
from failure_injection.scenarios import set_active_scenario
from mcp.tools.dagster import get_failed_assets_tool, get_asset_lineage_tool
from mcp.tools.dbt import get_failed_dbt_tests_tool
from mcp.tools.incidents import get_diagnosis_tool, list_incidents_tool

def test_full_mcp_incident_resolution_flow():
    # 1. Inject failure scenario
    set_active_scenario("null_customer_id")

    # 2. Query MCP tool: get_failed_assets()
    failed_assets_res = get_failed_assets_tool()
    assert "assets" in failed_assets_res
    failed_names = [a["name"] for a in failed_assets_res["assets"]]
    assert "stg_orders" in failed_names

    # 3. Query MCP tool: get_failed_dbt_tests()
    failed_tests_res = get_failed_dbt_tests_tool()
    assert len(failed_tests_res["failed_tests"]) > 0
    test_names = [t["name"] for t in failed_tests_res["failed_tests"]]
    assert any("not_null" in name for name in test_names)

    # 4. Query MCP tool: get_asset_lineage("stg_orders")
    lineage_res = get_asset_lineage_tool("stg_orders")
    assert lineage_res["asset"] == "stg_orders"
    assert "raw_orders" in lineage_res["upstream"]

    # 5. Query MCP tool: get_diagnosis()
    diagnosis_res = get_diagnosis_tool()
    assert diagnosis_res["status"] == "DIAGNOSED"
    assert diagnosis_res["confidence"] == 0.95
    assert "NULL customer_id" in diagnosis_res["root_cause"]
    assert len(diagnosis_res["evidence"]) > 0
    assert len(diagnosis_res["recommended_actions"]) > 0

    # Clean up
    set_active_scenario(None)
