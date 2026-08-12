import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

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
from mcp.tools.remediation import (
    propose_remediation_tool,
    validate_remediation_tool,
    get_remediation_plan_tool,
    get_remediation_status_tool,
    get_verification_result_tool
)

logger = logging.getLogger("dataops.mcp.server")


@dataclass
class RegisteredTool:
    name: str
    description: str
    parameters: Dict[str, Any]
    fn: Callable[..., Dict[str, Any]]


class ToolManager:
    def __init__(self):
        self._tools: List[RegisteredTool] = []

    def register(
        self,
        *,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        fn: Callable[..., Dict[str, Any]]
    ) -> None:
        self._tools.append(
            RegisteredTool(
                name=name,
                description=description,
                parameters=parameters,
                fn=fn
            )
        )

    def list_tools(self) -> List[RegisteredTool]:
        return list(self._tools)


class DataOpsMCPServer:
    """
    Lightweight in-process MCP-compatible registry used by the agent and tests.

    The project package is named ``mcp``, which collides with the third-party MCP
    SDK package. Keeping the tiny registry local avoids fragile sys.modules
    rewriting while preserving the decorator API this project uses.
    """
    def __init__(self, name: str):
        self.name = name
        self._tool_manager = ToolManager()

    def tool(self, *, name: str, description: str):
        def decorator(fn: Callable[..., Dict[str, Any]]):
            annotations = getattr(fn, "__annotations__", {})
            parameters = {
                key: str(value)
                for key, value in annotations.items()
                if key != "return"
            }
            self._tool_manager.register(
                name=name,
                description=description,
                parameters=parameters,
                fn=fn
            )
            return fn

        return decorator

    def run(self, transport: str = "stdio") -> None:
        logger.info(
            "DataOps MCP Server '%s' ready on %s with %d registered tools.",
            self.name,
            transport,
            len(self._tool_manager.list_tools())
        )


app = DataOpsMCPServer("DataOps-MCP-Server")

# --- Register Dagster Tools ---
@app.tool(
    name="get_failed_assets",
    description="Returns currently failed Dagster assets and relevant failure metadata. Use this when investigating pipeline execution stops."
)
def get_failed_assets() -> Dict[str, Any]:
    return get_failed_assets_tool()

@app.tool(
    name="get_asset_status",
    description="Returns the current status, latest successful run, latest failed run, and execution metadata for a specific Dagster asset."
)
def get_asset_status(asset_name: str) -> Dict[str, Any]:
    return get_asset_status_tool(asset_name)

@app.tool(
    name="get_asset_lineage",
    description="Returns upstream and downstream dependency relationships for a specific asset. Use this during incident diagnosis to trace root-cause failures back to upstream source assets or evaluate downstream impact."
)
def get_asset_lineage(asset_name: str) -> Dict[str, Any]:
    return get_asset_lineage_tool(asset_name)

@app.tool(
    name="get_recent_runs",
    description="Returns recent execution history runs for a given asset. Use this to determine if an asset failure is transient or recurring across multiple runs."
)
def get_recent_runs(asset_name: str, limit: int = 5) -> Dict[str, Any]:
    return get_recent_runs_tool(asset_name, limit)

@app.tool(
    name="get_asset_checks",
    description="Returns Dagster asset-check metrics and assertions for a specified asset. Use this to check runtime row count validations and data quality assertions."
)
def get_asset_checks(asset_name: str) -> Dict[str, Any]:
    return get_asset_checks_tool(asset_name)

# --- Register dbt Tools ---
@app.tool(
    name="get_dbt_test_results",
    description="Returns all dbt data quality test results across the project. Use this to review test suite execution results and identify passing/failing assertions."
)
def get_dbt_test_results() -> Dict[str, Any]:
    return get_dbt_test_results_tool()

@app.tool(
    name="get_dbt_model_status",
    description="Returns status, materialization strategy, schema, and column list for a specific dbt model. Use this when verifying dbt model compilation and target schema mapping."
)
def get_dbt_model_status(model_name: str) -> Dict[str, Any]:
    return get_dbt_model_status_tool(model_name)

@app.tool(
    name="get_failed_dbt_tests",
    description="Returns ONLY dbt tests that have failed in the latest pipeline run. Use this during incident investigation to pinpoint exact data quality test assertion failures."
)
def get_failed_dbt_tests() -> Dict[str, Any]:
    return get_failed_dbt_tests_tool()

# --- Register Incident Tools ---
@app.tool(
    name="list_incidents",
    description="Returns a list of all pipeline incidents detected and recorded by the platform. Use this to retrieve active or historical incident IDs and severity levels."
)
def list_incidents() -> Dict[str, Any]:
    return list_incidents_tool()

@app.tool(
    name="get_incident",
    description="Returns the complete incident object for a given incident_id. Use this when full incident details, severity, status, and affected assets are required."
)
def get_incident(incident_id: str) -> Dict[str, Any]:
    return get_incident_tool(incident_id)

@app.tool(
    name="get_incident_evidence",
    description="Returns collected evidence statements for a specific incident. Use this to review error signals, failed dbt tests, and database assertions linked to an incident."
)
def get_incident_evidence(incident_id: str) -> Dict[str, Any]:
    return get_incident_evidence_tool(incident_id)

@app.tool(
    name="get_diagnosis",
    description="Returns a deterministic incident diagnosis report containing root cause analysis, evidence, impact statement, and recommended remediation actions. Use this when formulating an incident explanation or proposing operator remediation steps."
)
def get_diagnosis(incident_id: Optional[str] = None) -> Dict[str, Any]:
    return get_diagnosis_tool(incident_id)

# --- Register Database Tools ---
@app.tool(
    name="get_table_stats",
    description="Returns row count and metadata for an approved table in the database (e.g. 'staging.stg_orders', 'marts.fct_orders'). Use this to inspect table volume and verify non-emptiness without executing raw SQL queries."
)
def get_table_stats(table_name: str) -> Dict[str, Any]:
    return get_table_stats_tool(table_name)

@app.tool(
    name="get_column_stats",
    description="Returns column statistics such as data type, null counts, and distinct counts for a column in an approved table. Use this during data quality investigation to check NULL ratios or distinct key cardinality."
)
def get_column_stats(table_name: str, column_name: str) -> Dict[str, Any]:
    return get_column_stats_tool(table_name, column_name)

@app.tool(
    name="get_recent_data_quality_stats",
    description="Returns aggregate data quality health metrics and issue summaries for a specified table. Use this to retrieve table quality scores and quality assertion histories."
)
def get_recent_data_quality_stats(table_name: str) -> Dict[str, Any]:
    return get_recent_data_quality_stats_tool(table_name)

# --- Register Ingestion Tools ---
@app.tool(
    name="get_ingestion_status",
    description="Returns latest dlt ingestion pipeline execution status, timestamp, and destination metadata. Use this to verify if the raw extraction and loading step completed successfully."
)
def get_ingestion_status() -> Dict[str, Any]:
    return get_ingestion_status_tool()

@app.tool(
    name="get_ingestion_metadata",
    description="Returns detailed extraction record counts per dataset resource (customers, products, orders, payments) and active failure scenarios. Use this when investigating source batch volumes or checking if failure injection scenario is active."
)
def get_ingestion_metadata() -> Dict[str, Any]:
    return get_ingestion_metadata_tool()

# --- Register Remediation Proposal Tools ---
@app.tool(
    name="propose_remediation",
    description="Proposes a structured remediation plan for an incident based on AI Agent diagnosis recommendations. The plan is registered in PENDING_APPROVAL status for human review."
)
def propose_remediation(incident_id: str) -> Dict[str, Any]:
    return propose_remediation_tool(incident_id)

@app.tool(
    name="validate_remediation",
    description="Validates a proposed remediation plan against safety rules, allowlists, and idempotency guarantees."
)
def validate_remediation(plan_id: str) -> Dict[str, Any]:
    return validate_remediation_tool(plan_id)

@app.tool(
    name="get_remediation_plan",
    description="Retrieves the complete remediation plan object by plan_id."
)
def get_remediation_plan(plan_id: str) -> Dict[str, Any]:
    return get_remediation_plan_tool(plan_id)

@app.tool(
    name="get_remediation_status",
    description="Returns the current status, approval metadata, and execution result for a remediation plan."
)
def get_remediation_status(plan_id: str) -> Dict[str, Any]:
    return get_remediation_status_tool(plan_id)

@app.tool(
    name="get_verification_result",
    description="Retrieves the post-execution recovery verification result for a remediation plan."
)
def get_verification_result(plan_id: str) -> Dict[str, Any]:
    return get_verification_result_tool(plan_id)


def start_server():
    logger.info("Starting DataOps MCP Server on stdio transport...")
    app.run(transport="stdio")

if __name__ == "__main__":
    start_server()
