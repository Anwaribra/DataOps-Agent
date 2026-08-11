from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    INVESTIGATING = "INVESTIGATING"
    ANALYZING = "ANALYZING"
    DIAGNOSED = "DIAGNOSED"
    RECOMMENDATION_READY = "RECOMMENDATION_READY"
    FAILED = "FAILED"


class AgentState(BaseModel):
    incident_id: str
    status: AgentStatus = AgentStatus.INITIALIZING
    objective: str = "Investigate DataOps incident and determine root cause using MCP tools"
    step_count: int = 0
    tool_call_count: int = 0
    max_tool_calls: int = Field(default=15)
    max_steps: int = Field(default=10)
    observed_evidence: List[str] = Field(default_factory=list)
    inferences: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    confidence_level: str = "LOW"
    uncertainty_notes: List[str] = Field(default_factory=list)
    trace: List[Dict[str, Any]] = Field(default_factory=list)


class AgentDiagnosis(BaseModel):
    incident_id: str
    severity: str
    status: str
    root_cause: str
    confidence: float
    confidence_level: str
    observed_evidence: List[str]
    inferences: List[str]
    impact: str
    recommended_actions: List[str]
    investigation_trace: List[Dict[str, Any]]
    uncertainty_notes: List[str]
    execution_halted: bool = True
    halt_reason: str = "Recommendation generated. No action executed. Human approval required."

    def to_formatted_report(self) -> str:
        """Formats the diagnosis into the required user-facing markdown text."""
        trace_lines = []
        for idx, step in enumerate(self.investigation_trace, 1):
            tool = step.get("tool_name", "unknown")
            reason = step.get("reason", "Investigating asset failure")
            summary = step.get("result_summary", "Completed successfully")
            trace_lines.append(f"  {idx}. {tool} → {summary}")

        evidence_bullets = "\n".join([f"- {ev}" for ev in self.observed_evidence]) or "- None"
        inferences_bullets = "\n".join([f"- {inf}" for inf in self.inferences]) or "- None"
        action_bullets = "\n".join([f"{idx+1}. {act}" for idx, act in enumerate(self.recommended_actions)]) or "1. Maintain normal pipeline monitoring"
        trace_str = "\n".join(trace_lines) or "  1. get_diagnosis → Retrieved active failure scenario evidence"

        return f"""
============================================================
              DATAOPS AI AGENT INCIDENT REPORT              
============================================================
Incident ID:          {self.incident_id}
Severity:             {self.severity.upper()}
Status:               {self.status}
Confidence Score:     {self.confidence * 100:.1f}% ({self.confidence_level})

Root Cause:
  {self.root_cause}

Observed Evidence (Facts):
{evidence_bullets}

Inferences (Reasoning):
{inferences_bullets}

Impact:
  {self.impact}

Recommended Actions (Pending Approval):
{action_bullets}

Investigation Trace:
{trace_str}

Uncertainty / Missing Evidence:
  {', '.join(self.uncertainty_notes) if self.uncertainty_notes else 'None. Evidence is sufficient for diagnosis.'}

------------------------------------------------------------
{self.halt_reason}
============================================================
"""
