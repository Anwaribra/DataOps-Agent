import logging
from typing import Dict, Any, Optional
from diagnosis.engine import get_incident_by_id
from mcp.schemas import MCPErrorResponse
from remediation.approval import approval_service
from remediation.planner import planner
from remediation.validator import validator

logger = logging.getLogger("dataops.mcp.tools.remediation")


def propose_remediation_tool(incident_id: str) -> Dict[str, Any]:
    """
    Proposes a structured remediation plan for an incident based on AI Agent diagnosis recommendations.
    The plan is registered in PENDING_APPROVAL status for human review.
    """
    try:
        inc = get_incident_by_id(incident_id)
        from agent.agent import DataOpsAgent
        agent = DataOpsAgent()
        diagnosis = agent.investigate(incident_id)

        plan = planner.create_plan_from_diagnosis(diagnosis)
        approval_service.register_plan(plan)

        return plan.model_dump()
    except Exception as e:
        logger.error(f"Error in propose_remediation_tool for {incident_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="propose_remediation", requested_input={"incident_id": incident_id}).model_dump()


def validate_remediation_tool(plan_id: str) -> Dict[str, Any]:
    """
    Validates a proposed remediation plan against safety rules, allowlists, and idempotency guarantees.
    """
    try:
        plan = approval_service.get_plan(plan_id)
        if not plan:
            return MCPErrorResponse(error=f"Plan '{plan_id}' not found.", tool_name="validate_remediation", requested_input={"plan_id": plan_id}).model_dump()
        return validator.validate_plan(plan)
    except Exception as e:
        logger.error(f"Error in validate_remediation_tool for {plan_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="validate_remediation", requested_input={"plan_id": plan_id}).model_dump()


def get_remediation_plan_tool(plan_id: str) -> Dict[str, Any]:
    """
    Retrieves the complete remediation plan object by plan_id.
    """
    try:
        plan = approval_service.get_plan(plan_id)
        if not plan:
            return MCPErrorResponse(error=f"Plan '{plan_id}' not found.", tool_name="get_remediation_plan", requested_input={"plan_id": plan_id}).model_dump()
        return plan.model_dump()
    except Exception as e:
        logger.error(f"Error in get_remediation_plan_tool for {plan_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_remediation_plan", requested_input={"plan_id": plan_id}).model_dump()


def get_remediation_status_tool(plan_id: str) -> Dict[str, Any]:
    """
    Returns the current status, approval metadata, and execution result for a remediation plan.
    """
    try:
        plan = approval_service.get_plan(plan_id)
        if not plan:
            return MCPErrorResponse(error=f"Plan '{plan_id}' not found.", tool_name="get_remediation_status", requested_input={"plan_id": plan_id}).model_dump()
        return {
            "plan_id": plan.plan_id,
            "incident_id": plan.incident_id,
            "status": plan.status.value,
            "approved_by": plan.approved_by,
            "approved_at": plan.approved_at,
            "expires_at": plan.expires_at,
            "is_valid": approval_service.is_approval_valid(plan) if plan.status == "APPROVED" else False
        }
    except Exception as e:
        logger.error(f"Error in get_remediation_status_tool for {plan_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_remediation_status", requested_input={"plan_id": plan_id}).model_dump()


def get_verification_result_tool(plan_id: str) -> Dict[str, Any]:
    """
    Retrieves the post-execution recovery verification result for a remediation plan.
    """
    try:
        plan = approval_service.get_plan(plan_id)
        if not plan:
            return MCPErrorResponse(error=f"Plan '{plan_id}' not found.", tool_name="get_verification_result", requested_input={"plan_id": plan_id}).model_dump()
        
        from remediation.verifier import verifier
        result = verifier.verify_recovery(plan)
        return result.model_dump()
    except Exception as e:
        logger.error(f"Error in get_verification_result_tool for {plan_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_verification_result", requested_input={"plan_id": plan_id}).model_dump()
