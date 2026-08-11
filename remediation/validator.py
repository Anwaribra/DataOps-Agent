import logging
from typing import Any, Dict, List
from remediation.actions import ALLOWLISTED_ASSETS
from remediation.models import ActionType, RemediationAction, RemediationPlan, RiskLevel
from mcp.context import context

logger = logging.getLogger("dataops.remediation.validator")


class ValidationResult(BaseModel := type('ValidationResult', (), {})):
    pass

class RemediationValidator:
    """
    Validates remediation plans against strict allowlists, safety rules, and idempotency guarantees.
    """
    def validate_plan(self, plan: RemediationPlan) -> Dict[str, Any]:
        logger.info(f"Validating remediation plan '{plan.plan_id}' for incident '{plan.incident_id}'...")

        if not plan.actions:
            return {"valid": False, "reason": "Plan contains no remediation actions."}

        action_results = []
        for act in plan.actions:
            res = self.validate_action(act, plan.incident_id)
            action_results.append(res)
            if not res["valid"]:
                logger.error(f"Plan validation failed on action '{act.action_id}': {res['reason']}")
                return {"valid": False, "reason": f"Action '{act.action_type.value}' invalid: {res['reason']}"}

        logger.info(f"Plan '{plan.plan_id}' validated successfully.")
        return {
            "valid": True,
            "plan_id": plan.plan_id,
            "incident_id": plan.incident_id,
            "actions_validated": len(action_results),
            "overall_risk": plan.risk_level.value
        }

    def validate_action(self, action: RemediationAction, incident_id: str) -> Dict[str, Any]:
        # 1. Action type check
        if action.action_type not in (ActionType.RERUN_DAGSTER_ASSET, ActionType.QUARANTINE_INVALID_RECORDS, ActionType.REFRESH_DBT_MODEL):
            return {"valid": False, "reason": f"Action type '{action.action_type}' is forbidden or not allowlisted."}

        # 2. Target allowlist check
        target = action.target.strip().lower()
        if action.action_type in (ActionType.RERUN_DAGSTER_ASSET, ActionType.REFRESH_DBT_MODEL):
            if target not in ALLOWLISTED_ASSETS:
                return {"valid": False, "reason": f"Target asset/model '{target}' is not in approved allowlist."}
        elif action.action_type == ActionType.QUARANTINE_INVALID_RECORDS:
            if not context.is_table_allowed(target):
                return {"valid": False, "reason": f"Target table '{target}' is not in approved table registry."}

        # 3. Ensure idempotency key exists
        if not action.idempotency_key:
            action.idempotency_key = f"{incident_id}_{action.action_id}"

        return {
            "valid": True,
            "action_id": action.action_id,
            "action_type": action.action_type.value,
            "target": target,
            "idempotency_key": action.idempotency_key
        }


# Singleton instance
validator = RemediationValidator()
