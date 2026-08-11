import logging
from typing import Dict, Any, List
from mcp.context import context
from mcp.schemas import (
    GetDbtTestResultsOutput, DbtTestDetail,
    GetDbtModelStatusOutput,
    GetFailedDbtTestsOutput,
    MCPErrorResponse
)

logger = logging.getLogger("dataops.mcp.tools.dbt")

def get_dbt_test_results_tool() -> Dict[str, Any]:
    """
    Returns all dbt data quality test results across the project.
    Use this to review test suite execution results and identify passing/failing assertions.
    """
    try:
        raw_results = context.get_dbt_test_results()
        tests = []
        for r in raw_results:
            tests.append(
                DbtTestDetail(
                    name=r.get("test_name", "unknown_test"),
                    model="stg_orders" if "stg_orders" in r.get("test_name", "") else "fct_orders",
                    status="FAIL" if r.get("status") == "fail" else "PASS",
                    failures=r.get("failures", 1 if r.get("status") == "fail" else 0),
                    message=r.get("message")
                )
            )
        return GetDbtTestResultsOutput(tests=tests).model_dump()
    except Exception as e:
        logger.error(f"Error in get_dbt_test_results_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_dbt_test_results").model_dump()

def get_dbt_model_status_tool(model_name: str) -> Dict[str, Any]:
    """
    Returns status, materialization strategy, schema, and column list for a specific dbt model.
    Use this when verifying dbt model compilation and target schema mapping.
    """
    try:
        clean_name = model_name.lower().strip()
        materialization = "view" if clean_name.startswith("stg_") or clean_name.startswith("int_") else "table"
        schema = "staging" if clean_name.startswith("stg_") else ("intermediate" if clean_name.startswith("int_") else "marts")
        
        failed_assets = context.get_failed_assets()
        status = "ERROR" if clean_name in failed_assets else "SUCCESS"

        columns_map = {
            "stg_customers": ["customer_id", "first_name", "last_name", "email", "created_at", "status"],
            "stg_orders": ["order_id", "customer_id", "order_date", "status", "total_amount", "payment_method"],
            "fct_orders": ["order_id", "customer_id", "order_date", "order_status", "total_amount", "paid_amount"]
        }
        cols = columns_map.get(clean_name, ["id", "created_at", "updated_at"])

        return GetDbtModelStatusOutput(
            model_name=clean_name,
            status=status,
            materialization=materialization,
            schema_name=schema,
            columns=cols
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_dbt_model_status_tool for {model_name}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_dbt_model_status", requested_input={"model_name": model_name}).model_dump()

def get_failed_dbt_tests_tool() -> Dict[str, Any]:
    """
    Returns ONLY dbt tests that have failed in the latest pipeline run.
    Use this during incident investigation to pinpoint exact data quality test assertion failures.
    """
    try:
        all_results = get_dbt_test_results_tool()
        if "error" in all_results:
            return all_results
        
        tests = all_results.get("tests", [])
        failed = [DbtTestDetail(**t) for t in tests if t.get("status") == "FAIL"]
        return GetFailedDbtTestsOutput(failed_tests=failed).model_dump()
    except Exception as e:
        logger.error(f"Error in get_failed_dbt_tests_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_failed_dbt_tests").model_dump()
