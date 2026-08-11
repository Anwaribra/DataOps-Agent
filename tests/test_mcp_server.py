import pytest
from mcp.server import app

def test_mcp_server_initialization():
    assert app.name == "DataOps-MCP-Server"

def test_mcp_tools_registered():
    tools = app._tool_manager.list_tools()
    tool_names = [t.name for t in tools]
    
    expected_tools = [
        "get_failed_assets", "get_asset_status", "get_asset_lineage", "get_recent_runs", "get_asset_checks",
        "get_dbt_test_results", "get_dbt_model_status", "get_failed_dbt_tests",
        "list_incidents", "get_incident", "get_incident_evidence", "get_diagnosis",
        "get_table_stats", "get_column_stats", "get_recent_data_quality_stats",
        "get_ingestion_status", "get_ingestion_metadata"
    ]
    
    for tool_name in expected_tools:
        assert tool_name in tool_names, f"Tool '{tool_name}' missing from MCP server registration."

def test_no_arbitrary_sql_tool_registered():
    tools = app._tool_manager.list_tools()
    tool_names = [t.name for t in tools]
    assert "execute_sql" not in tool_names, "Security Error: Arbitrary execute_sql tool must not be exposed."
