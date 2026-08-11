import logging
from typing import Dict, Any, List
from mcp.context import context
from mcp.schemas import (
    GetFailedAssetsOutput, AssetSummary,
    GetAssetStatusOutput,
    GetAssetLineageOutput,
    GetRecentRunsOutput, RunSummary,
    GetAssetChecksOutput, AssetCheckDetail,
    MCPErrorResponse
)

logger = logging.getLogger("dataops.mcp.tools.dagster")

def get_failed_assets_tool() -> Dict[str, Any]:
    """
    Returns currently failed Dagster assets and relevant metadata.
    Use this when investigating whether pipeline execution has stopped due to asset failure.
    """
    try:
        failed_names = context.get_failed_assets()
        summaries = [
            AssetSummary(
                name=name,
                status="FAILED",
                last_run="2026-02-25T12:00:00Z",
                failure_reason="dbt_test_or_asset_check_failed"
            )
            for name in failed_names
        ]
        return GetFailedAssetsOutput(assets=summaries).model_dump()
    except Exception as e:
        logger.error(f"Error in get_failed_assets_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_failed_assets").model_dump()

def get_asset_status_tool(asset_name: str) -> Dict[str, Any]:
    """
    Returns the current status, latest successful run, latest failed run, and execution metadata for a specific Dagster asset.
    Use this when verifying if a specific asset (e.g. 'stg_orders', 'fct_orders') is healthy or degraded.
    """
    try:
        failed_assets = context.get_failed_assets()
        is_failed = asset_name in failed_assets
        status = "FAILED" if is_failed else "SUCCESS"
        
        return GetAssetStatusOutput(
            asset_name=asset_name,
            status=status,
            last_successful_run="2026-02-24T12:00:00Z" if is_failed else "2026-02-25T12:00:00Z",
            last_failed_run="2026-02-25T12:00:00Z" if is_failed else None,
            latest_run="2026-02-25T12:00:00Z",
            metadata={"group": "transformation" if "stg_" in asset_name or "fct_" in asset_name else "ingestion"}
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_asset_status_tool for {asset_name}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_asset_status", requested_input={"asset_name": asset_name}).model_dump()

def get_asset_lineage_tool(asset_name: str) -> Dict[str, Any]:
    """
    Returns upstream and downstream dependency relationships for a specific asset.
    Use this during incident diagnosis to trace root-cause failures back to upstream source assets or evaluate downstream impact.
    """
    try:
        lineage = context.get_asset_lineage(asset_name)
        return GetAssetLineageOutput(
            asset=asset_name,
            upstream=lineage.get("upstream", []),
            downstream=lineage.get("downstream", [])
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_asset_lineage_tool for {asset_name}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_asset_lineage", requested_input={"asset_name": asset_name}).model_dump()

def get_recent_runs_tool(asset_name: str, limit: int = 5) -> Dict[str, Any]:
    """
    Returns recent execution history runs for a given asset.
    Use this to determine if an asset failure is transient or recurring across multiple runs.
    """
    try:
        runs_data = context.get_recent_runs(asset_name, limit=limit)
        run_summaries = [RunSummary(**r) for r in runs_data]
        return GetRecentRunsOutput(asset_name=asset_name, runs=run_summaries).model_dump()
    except Exception as e:
        logger.error(f"Error in get_recent_runs_tool for {asset_name}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_recent_runs", requested_input={"asset_name": asset_name, "limit": limit}).model_dump()

def get_asset_checks_tool(asset_name: str) -> Dict[str, Any]:
    """
    Returns Dagster asset-check metrics and assertions for a specified asset.
    Use this to check runtime row count validations and data quality assertions.
    """
    try:
        failed_assets = context.get_failed_assets()
        check_status = "PASSED"
        if asset_name in failed_assets:
            check_status = "FAILED"
            
        checks = [
            AssetCheckDetail(
                check_name=f"{asset_name}_row_count_check",
                asset_name=asset_name,
                status=check_status,
                description=f"Verifies row count non-emptiness for {asset_name}"
            )
        ]
        return GetAssetChecksOutput(asset_name=asset_name, checks=checks).model_dump()
    except Exception as e:
        logger.error(f"Error in get_asset_checks_tool for {asset_name}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_asset_checks", requested_input={"asset_name": asset_name}).model_dump()
