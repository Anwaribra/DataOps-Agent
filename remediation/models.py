import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    PROPOSED = "PROPOSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ActionType(str, Enum):
    RERUN_DAGSTER_ASSET = "rerun_dagster_asset"
    QUARANTINE_INVALID_RECORDS = "quarantine_invalid_records"
    REFRESH_DBT_MODEL = "refresh_dbt_model"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}")
    action_type: ActionType
    target: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reason: str
    expected_result: str = "Target asset restored cleanly."
    risk_level: RiskLevel = RiskLevel.LOW
    idempotency_key: Optional[str] = None


class RemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    incident_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: str = "DATAOPS_AGENT"
    reason: str
    actions: List[RemediationAction] = Field(default_factory=list)
    expected_outcome: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    status: PlanStatus = PlanStatus.PROPOSED
    approval_id: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    expires_at: Optional[str] = None
    execution_result: Dict[str, Any] = Field(default_factory=dict)
