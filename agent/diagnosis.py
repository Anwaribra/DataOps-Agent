"""
Incident Diagnosis Data Models and Structures (Phase 2).
"""

from typing import List, Optional
from pydantic import BaseModel

class IncidentReport(BaseModel):
    incident_id: str
    failed_asset: str
    failure_type: str
    root_cause: str
    evidence: List[str]
    proposed_remediation: str
    requires_human_approval: bool = True
