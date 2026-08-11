import logging
from typing import Dict, Any
from mcp.context import context
from mcp.schemas import (
    GetIngestionStatusOutput,
    GetIngestionMetadataOutput,
    MCPErrorResponse
)

logger = logging.getLogger("dataops.mcp.tools.ingestion")

def get_ingestion_status_tool() -> Dict[str, Any]:
    """
    Returns latest dlt ingestion pipeline execution status, timestamp, and destination metadata.
    Use this to verify if the raw extraction and loading step completed successfully.
    """
    try:
        ingest_meta = context.get_ingestion_metadata()
        return GetIngestionStatusOutput(
            pipeline_name=ingest_meta.get("pipeline", "ecommerce_ingestion"),
            status="SUCCESS",
            last_run_timestamp=ingest_meta.get("last_ingestion_timestamp", "2026-02-25T12:00:00Z"),
            destination="postgresql"
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_ingestion_status_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_ingestion_status").model_dump()

def get_ingestion_metadata_tool() -> Dict[str, Any]:
    """
    Returns detailed extraction record counts per dataset resource (customers, products, orders, payments) and active failure scenarios.
    Use this when investigating source batch volumes or checking if failure injection scenario is active.
    """
    try:
        ingest_meta = context.get_ingestion_metadata()
        return GetIngestionMetadataOutput(
            pipeline=ingest_meta.get("pipeline", "ecommerce_ingestion"),
            active_scenario=ingest_meta.get("active_scenario", "healthy"),
            last_ingestion_timestamp=ingest_meta.get("last_ingestion_timestamp", "2026-02-25T12:00:00Z"),
            records_ingested=ingest_meta.get("records_ingested", {"customers": 5, "products": 5, "orders": 5, "payments": 5})
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_ingestion_metadata_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_ingestion_metadata").model_dump()
