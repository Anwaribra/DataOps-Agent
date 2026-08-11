import pytest
from agent.client import DataOpsMCPClient

def test_mcp_client_connect_and_tool_discovery():
    client = DataOpsMCPClient()
    connected = client.connect()
    assert connected is True
    assert client.connected is True

    tools = client.list_tools()
    assert len(tools) >= 16
    tool_names = [t["name"] for t in tools]
    assert "get_failed_assets" in tool_names
    assert "get_failed_dbt_tests" in tool_names
    assert "get_diagnosis" in tool_names

def test_mcp_client_call_tool_delegation():
    client = DataOpsMCPClient()
    client.connect()
    
    res = client.call_tool("get_failed_assets")
    assert "assets" in res

    res_lineage = client.call_tool("get_asset_lineage", {"asset_name": "stg_orders"})
    assert res_lineage["asset"] == "stg_orders"
    assert "raw_orders" in res_lineage["upstream"]

def test_mcp_client_invalid_tool_handling():
    client = DataOpsMCPClient()
    client.connect()
    res = client.call_tool("invalid_non_existent_tool")
    assert "error" in res
    assert "not found" in res["error"]
