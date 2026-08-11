from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field
from health.models import HealthSignal, Severity


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    DIAGNOSED = "DIAGNOSED"
    RECOMMENDATION_READY = "RECOMMENDATION_READY"
    RESOLVED = "RESOLVED"


class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"inc_{uuid.uuid4().hex[:8]}")
    status: IncidentStatus = IncidentStatus.DETECTED
    severity: Severity = Severity.HIGH
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    affected_assets: List[str] = Field(default_factory=list)
    signals: List[HealthSignal] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    probable_root_cause: str = "Under investigation"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    impact: str = "Unspecified impact"
    recommended_actions: List[str] = Field(default_factory=list)
