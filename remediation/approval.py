import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from remediation.audit import audit_logger
from remediation.models import PlanStatus, RemediationPlan

logger = logging.getLogger("dataops.remediation.approval")

TTL_MINUTES = int(os.getenv("REMEDIATION_APPROVAL_TTL_MINUTES", "30"))


class ApprovalService:
    """
    Manages human approval workflows, prevents agent self-approval, and enforces TTL expiration.
    """
    def __init__(self):
        self._plans: Dict[str, RemediationPlan] = {}

    def register_plan(self, plan: RemediationPlan):
        self._plans[plan.plan_id] = plan
        logger.info(f"Registered plan '{plan.plan_id}' for incident '{plan.incident_id}'. Status: {plan.status.value}")

    def get_plan(self, plan_id: str) -> Optional[RemediationPlan]:
        return self._plans.get(plan_id)

    def list_plans(self) -> List[RemediationPlan]:
        return list(self._plans.values())

    def approve_plan(self, plan_id: str, approver: str = "HUMAN_OPERATOR") -> RemediationPlan:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Remediation plan '{plan_id}' not found.")

        # Safety Check 1: Prevent Agent Self-Approval
        if approver.upper() in ("DATAOPS_AGENT", "AGENT", "AI_AGENT"):
            raise ValueError("Security Violation: AI Agent is forbidden from approving its own remediation plan.")

        # Safety Check 2: Verify current status
        if plan.status not in (PlanStatus.PENDING_APPROVAL, PlanStatus.PROPOSED):
            raise ValueError(f"Plan '{plan_id}' cannot be approved because current status is '{plan.status.value}'.")

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=TTL_MINUTES)

        plan.status = PlanStatus.APPROVED
        plan.approval_id = f"appr_{uuid.uuid4().hex[:8]}"
        plan.approved_at = now.isoformat()
        plan.approved_by = approver
        plan.expires_at = expires_at.isoformat()

        audit_logger.log_event(
            event_type="remediation_approved",
            incident_id=plan.incident_id,
            plan_id=plan.plan_id,
            actor=approver,
            status="APPROVED",
            metadata={"expires_at": plan.expires_at, "approval_id": plan.approval_id}
        )

        logger.info(f"Plan '{plan_id}' APPROVED by {approver}. Expires at {plan.expires_at}")
        return plan

    def reject_plan(self, plan_id: str, approver: str = "HUMAN_OPERATOR", reason: str = "Operator rejected plan") -> RemediationPlan:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Remediation plan '{plan_id}' not found.")

        plan.status = PlanStatus.REJECTED

        audit_logger.log_event(
            event_type="remediation_rejected",
            incident_id=plan.incident_id,
            plan_id=plan.plan_id,
            actor=approver,
            status="REJECTED",
            metadata={"reason": reason}
        )

        logger.info(f"Plan '{plan_id}' REJECTED by {approver}. Reason: {reason}")
        return plan

    def is_approval_valid(self, plan: RemediationPlan) -> bool:
        if plan.status != PlanStatus.APPROVED:
            return False
        if not plan.expires_at:
            return False
        
        expires_dt = datetime.fromisoformat(plan.expires_at)
        now_dt = datetime.now(timezone.utc)
        if now_dt > expires_dt:
            logger.warning(f"Plan '{plan.plan_id}' approval has EXPIRED.")
            return False
        return True


# Singleton instance
approval_service = ApprovalService()
