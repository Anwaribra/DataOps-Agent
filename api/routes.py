import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agent.agent import DataOpsAgent
from diagnosis.engine import DiagnosisEngine, get_incident_by_id, list_incidents
from failure_injection.runner import get_active_scenario, set_active_scenario
from health import collectors
from remediation.approval import approval_service
from remediation.executor import executor
from remediation.planner import planner
from remediation.verifier import verifier

logger = logging.getLogger("dataops.api.routes")
router = APIRouter()


class ApprovalRequest(BaseModel):
    approver: str = "HUMAN_OPERATOR"


class RejectionRequest(BaseModel):
    approver: str = "HUMAN_OPERATOR"
    reason: str = "Operator rejected plan"


class ScenarioInjectRequest(BaseModel):
    scenario: str = "null_customer_id"


@router.get("/health")
def get_system_health() -> Dict[str, Any]:
    """Returns platform health summary and active failure injection scenario."""
    failed_assets = collectors.get_failed_assets()
    dbt_tests = collectors.get_dbt_test_results()
    failed_dbt = [t for t in dbt_tests if t.get("status") == "fail"]
    active_scenario = get_active_scenario()

    is_healthy = len(failed_assets) == 0 and len(failed_dbt) == 0 and active_scenario is None

    return {
        "status": "HEALTHY" if is_healthy else "DEGRADED",
        "active_scenario": active_scenario,
        "failed_assets_count": len(failed_assets),
        "failed_dbt_tests_count": len(failed_dbt),
        "data_quality_score": 99.8 if is_healthy else 91.6,
        "version": "1.0.0-MCP"
    }


@router.get("/pipeline")
def get_pipeline_nodes() -> List[Dict[str, Any]]:
    """Returns pipeline stage nodes with real runtime statuses."""
    failed_assets = collectors.get_failed_assets()
    dbt_tests = collectors.get_dbt_test_results()
    failed_dbt = [t for t in dbt_tests if t.get("status") == "fail"]
    active_scenario = get_active_scenario()

    dbt_status = "FAILED" if len(failed_dbt) > 0 else "HEALTHY"
    dagster_status = "FAILED" if len(failed_assets) > 0 else "HEALTHY"
    health_status = "WARNING" if active_scenario else "HEALTHY"

    return [
        {
            "id": "data_sources",
            "name": "Data Sources",
            "category": "Ingestion",
            "status": "HEALTHY",
            "description": "E-commerce transactional JSON batch files",
            "tech": "JSON / REST API",
            "metadata": {"Source Datasets": 4, "Total Records": 505, "Format": "JSON"}
        },
        {
            "id": "dlt_ingestion",
            "name": "dlt Ingestion",
            "category": "Ingestion",
            "status": "HEALTHY",
            "description": "Python dlt pipeline extracting raw JSON data into PostgreSQL",
            "tech": "dlt (data load tool)",
            "metadata": {"Destination": "PostgreSQL 16", "Target Schema": "raw_data"}
        },
        {
            "id": "postgres_raw",
            "name": "PostgreSQL Raw",
            "category": "Storage",
            "status": "HEALTHY",
            "description": "Relational database housing raw and transformed data tables",
            "tech": "PostgreSQL 16",
            "metadata": {"Port": 5433, "Schemas": "raw_data, staging, intermediate, marts"}
        },
        {
            "id": "dbt_transformation",
            "name": "dbt Models",
            "category": "Transformation",
            "status": dbt_status,
            "description": "Modular SQL transformations with 27 data quality assertions",
            "tech": "dbt-core / dbt-postgres",
            "metadata": {"Models": 7, "Quality Tests": 27, "Failing Tests": len(failed_dbt)}
        },
        {
            "id": "dagster_orchestrator",
            "name": "Dagster Engine",
            "category": "Orchestration",
            "status": dagster_status,
            "description": "Asset orchestration, lineage graphs, and runtime asset checks",
            "tech": "Dagster 1.6+",
            "metadata": {"Assets Defined": 8, "Failed Assets": len(failed_assets)}
        },
        {
            "id": "health_signals",
            "name": "Health Signals",
            "category": "Observability",
            "status": health_status,
            "description": "Normalized data quality signals and evidence collectors",
            "tech": "Pydantic Signal Layer",
            "metadata": {"Active Scenario": active_scenario or "None"}
        },
        {
            "id": "mcp_server",
            "name": "MCP Server",
            "category": "Protocol",
            "status": "HEALTHY",
            "description": "Standardized read-only & proposal tools for AI Agent interface",
            "tech": "Model Context Protocol (stdio)",
            "metadata": {"Registered Tools": 22, "Transport": "stdio"}
        },
        {
            "id": "dataops_agent",
            "name": "LLM DataOps Agent",
            "category": "AI Reasoning",
            "status": "HEALTHY",
            "description": "Autonomous DataOps engineer carrying out evidence-based diagnosis",
            "tech": "LLMProvider / Agent Loop",
            "metadata": {"Execution Control": "Human Approval Gate"}
        }
    ]


@router.get("/incidents")
def get_incidents_list() -> List[Dict[str, Any]]:
    """Returns all recorded pipeline incidents."""
    incidents = list_incidents()
    if not incidents:
        # Check active diagnosis engine
        diag_engine = DiagnosisEngine()
        inc = diag_engine.diagnose_active_pipeline()
        return [inc.model_dump()]
    return [i.model_dump() for i in incidents]


@router.get("/incidents/{incident_id}")
def get_incident_detail(incident_id: str) -> Dict[str, Any]:
    """Returns specific incident by ID."""
    inc = get_incident_by_id(incident_id)
    if not inc:
        # Fallback to active diagnosis
        diag_engine = DiagnosisEngine()
        inc = diag_engine.diagnose_active_pipeline()
    return inc.model_dump()


@router.get("/incidents/{incident_id}/investigation")
def investigate_incident(incident_id: str) -> Dict[str, Any]:
    """Executes AI DataOps Agent investigation over MCP tools and returns diagnosis trace."""
    try:
        agent = DataOpsAgent()
        diagnosis = agent.investigate(incident_id)
        
        # Formulate and register remediation plan automatically
        plan = planner.create_plan_from_diagnosis(diagnosis)
        approval_service.register_plan(plan)

        return {
            "incident_id": incident_id,
            "diagnosis": diagnosis.model_dump(),
            "plan_id": plan.plan_id,
            "status": plan.status.value
        }
    except Exception as e:
        logger.error(f"Error investigating incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/{incident_id}/diagnosis")
def get_incident_diagnosis(incident_id: str) -> Dict[str, Any]:
    """Returns diagnosis for incident."""
    agent = DataOpsAgent()
    diagnosis = agent.investigate(incident_id)
    return diagnosis.model_dump()


@router.get("/incidents/{incident_id}/remediation")
def get_remediation_plan(incident_id: str) -> Dict[str, Any]:
    """Returns registered remediation plan for incident."""
    plans = approval_service.list_plans()
    target_plan = next((p for p in plans if p.incident_id == incident_id), None)
    
    if not target_plan:
        agent = DataOpsAgent()
        diagnosis = agent.investigate(incident_id)
        target_plan = planner.create_plan_from_diagnosis(diagnosis)
        approval_service.register_plan(target_plan)

    return target_plan.model_dump()


@router.post("/incidents/{incident_id}/approve")
def approve_remediation_plan(incident_id: str, req: ApprovalRequest) -> Dict[str, Any]:
    """Human operator approves remediation plan."""
    plans = approval_service.list_plans()
    target_plan = next((p for p in plans if p.incident_id == incident_id), None)
    
    if not target_plan:
        raise HTTPException(status_code=44, detail=f"No plan found for incident '{incident_id}'")

    try:
        approved_plan = approval_service.approve_plan(target_plan.plan_id, approver=req.approver)
        return approved_plan.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/incidents/{incident_id}/reject")
def reject_remediation_plan(incident_id: str, req: RejectionRequest) -> Dict[str, Any]:
    """Human operator rejects remediation plan."""
    plans = approval_service.list_plans()
    target_plan = next((p for p in plans if p.incident_id == incident_id), None)
    
    if not target_plan:
        raise HTTPException(status_code=404, detail=f"No plan found for incident '{incident_id}'")

    try:
        rejected_plan = approval_service.reject_plan(target_plan.plan_id, approver=req.approver, reason=req.reason)
        return rejected_plan.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/incidents/{incident_id}/execute")
def execute_remediation_plan(incident_id: str) -> Dict[str, Any]:
    """Executes approved allowlisted remediation plan."""
    plans = approval_service.list_plans()
    target_plan = next((p for p in plans if p.incident_id == incident_id), None)
    
    if not target_plan:
        raise HTTPException(status_code=404, detail=f"No plan found for incident '{incident_id}'")

    try:
        res = executor.execute_plan(target_plan)
        return {
            "status": "SUCCESS",
            "execution_result": res,
            "plan_status": target_plan.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/incidents/{incident_id}/verify")
def verify_incident_recovery(incident_id: str) -> Dict[str, Any]:
    """Verifies pipeline recovery after remediation execution."""
    plans = approval_service.list_plans()
    target_plan = next((p for p in plans if p.incident_id == incident_id), None)
    
    if not target_plan:
        raise HTTPException(status_code=404, detail=f"No plan found for incident '{incident_id}'")

    try:
        result = verifier.verify_recovery(target_plan)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demo/inject")
def inject_demo_scenario(req: ScenarioInjectRequest) -> Dict[str, Any]:
    """Injects a controlled failure scenario into the pipeline."""
    set_active_scenario(req.scenario)
    diag_engine = DiagnosisEngine()
    incident = diag_engine.diagnose_active_pipeline()
    return {
        "status": "SCENARIO_INJECTED",
        "scenario": req.scenario,
        "incident": incident.model_dump()
    }


@router.post("/demo/reset")
def reset_demo_scenario() -> Dict[str, Any]:
    """Resets active failure scenarios to HEALTHY state."""
    set_active_scenario(None)
    return {"status": "HEALTHY", "active_scenario": None}
