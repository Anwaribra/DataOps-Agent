import logging
from typing import Dict, Any, Optional
from mcp.context import context
from mcp.schemas import (
    ListIncidentsOutput, IncidentSummary,
    GetIncidentOutput,
    GetIncidentEvidenceOutput,
    GetDiagnosisOutput,
    MCPErrorResponse
)

logger = logging.getLogger("dataops.mcp.tools.incidents")

def list_incidents_tool() -> Dict[str, Any]:
    """
    Returns a list of all pipeline incidents detected and recorded by the platform.
    Use this to retrieve active or historical incident IDs and severity levels.
    """
    try:
        incidents = context.list_incidents()
        summaries = [
            IncidentSummary(
                incident_id=inc.incident_id,
                status=inc.status.value,
                severity=inc.severity.value,
                detected_at=inc.detected_at,
                affected_assets=inc.affected_assets,
                probable_root_cause=inc.probable_root_cause,
                confidence=inc.confidence
            )
            for inc in incidents
        ]
        return ListIncidentsOutput(incidents=summaries).model_dump()
    except Exception as e:
        logger.error(f"Error in list_incidents_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="list_incidents").model_dump()

def get_incident_tool(incident_id: str) -> Dict[str, Any]:
    """
    Returns the complete incident object for a given incident_id.
    Use this when full incident details, severity, status, and affected assets are required.
    """
    try:
        inc = context.get_incident(incident_id)
        if not inc:
            return MCPErrorResponse(
                error=f"Incident '{incident_id}' not found.",
                tool_name="get_incident",
                requested_input={"incident_id": incident_id}
            ).model_dump()
        return GetIncidentOutput(incident=inc.model_dump()).model_dump()
    except Exception as e:
        logger.error(f"Error in get_incident_tool for {incident_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_incident", requested_input={"incident_id": incident_id}).model_dump()

def get_incident_evidence_tool(incident_id: str) -> Dict[str, Any]:
    """
    Returns collected evidence statements for a specific incident.
    Use this to review error signals, failed dbt tests, and database assertions linked to an incident.
    """
    try:
        inc = context.get_incident(incident_id)
        if not inc:
            return MCPErrorResponse(
                error=f"Incident '{incident_id}' not found.",
                tool_name="get_incident_evidence",
                requested_input={"incident_id": incident_id}
            ).model_dump()
        return GetIncidentEvidenceOutput(
            incident_id=incident_id,
            evidence=inc.evidence
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_incident_evidence_tool for {incident_id}: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_incident_evidence", requested_input={"incident_id": incident_id}).model_dump()

def get_diagnosis_tool(incident_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a deterministic incident diagnosis report containing root cause analysis, evidence, impact statement, and recommended remediation actions.
    Use this when formulating an incident explanation or proposing operator remediation steps.
    """
    try:
        inc = context.get_diagnosis(incident_id)
        return GetDiagnosisOutput(
            incident_id=inc.incident_id,
            status=inc.status.value,
            severity=inc.severity.value,
            affected_assets=inc.affected_assets,
            root_cause=inc.probable_root_cause,
            confidence=inc.confidence,
            evidence=inc.evidence,
            impact=inc.impact,
            recommended_actions=inc.recommended_actions
        ).model_dump()
    except Exception as e:
        logger.error(f"Error in get_diagnosis_tool: {e}")
        return MCPErrorResponse(error=str(e), tool_name="get_diagnosis", requested_input={"incident_id": incident_id}).model_dump()
