"""
dbt MCP Tools Stub (Phase 2).
Provides functions to query dbt test failures and model compilation metadata.
"""

def get_dbt_test_failures():
    """Parse dbt target/run_results.json for failed tests."""
    raise NotImplementedError("Phase 2 tool")

def compile_dbt_model(model_name: str):
    """Compile specific dbt model SQL."""
    raise NotImplementedError("Phase 2 tool")
