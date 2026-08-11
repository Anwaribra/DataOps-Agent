import logging
import os
from typing import Any, Dict
from remediation.actions import (
    quarantine_invalid_records_action,
    refresh_dbt_model_action,
    rerun_dagster_asset_action
)
from remediation.approval import approval_service
from remediation.audit import audit_logger
from remediation.models import ActionType, PlanStatus, RemediationPlan
from remediation.validator import validator

logger = logging.getLogger("dataops.remediation.executor")


class RemediationExecutor:
    """
    Executes validated and approved remediation plans.
    Supports dry-run mode and logs full execution audit trails.
    """
    def __init__(self):
        self.dry_run = os.getenv("REMEDIATION_DRY_RUN", "false").lower() == "true"

    def execute_plan(self, plan: RemediationPlan) -> Dict[str, Any]:
        logger.info(f"Initiating execution for plan '{plan.plan_id}' (Dry Run: {self.dry_run})...")

        # 1. Verify approval status & TTL
        if not approval_service.is_approval_valid(plan):
            audit_logger.log_event(
                event_type="execution_failed",
                incident_id=plan.incident_id,
                plan_id=plan.plan_id,
                actor="SYSTEM",
                status="FAILED",
                metadata={"reason": "Plan is unapproved or approval has expired."}
            )
            raise ValueError(f"Execution Error: Plan '{plan.plan_id}' is unapproved or approval TTL has expired.")

        # 2. Validate plan rules
        validation = validator.validate_plan(plan)
        if not validation["valid"]:
            plan.status = PlanStatus.FAILED
            raise ValueError(f"Execution Error: Plan validation failed: {validation['reason']}")

        plan.status = PlanStatus.EXECUTING
        audit_logger.log_event(
            event_type="remediation_started",
            incident_id=plan.incident_id,
            plan_id=plan.plan_id,
            actor="SYSTEM",
            status="EXECUTING",
            metadata={"dry_run": self.dry_run}
        )

        action_results = []
        try:
            for act in plan.actions:
                if self.dry_run:
                    logger.info(f"DRY RUN: Simulating action '{act.action_type.value}' on target '{act.target}'")
                    res = {
                        "action": act.action_type.value,
                        "target": act.target,
                        "status": "SIMULATED_SUCCESS",
                        "dry_run": True
                    }
                else:
                    if act.action_type == ActionType.RERUN_DAGSTER_ASSET:
                        res = rerun_dagster_asset_action(act.target)
                    elif act.action_type == ActionType.QUARANTINE_INVALID_RECORDS:
                        res = quarantine_invalid_records_action(
                            table_name=act.target,
                            column_name=act.parameters.get("column_name", "customer_id"),
                            incident_id=plan.incident_id,
                            condition=act.parameters.get("condition")
                        )
                    elif act.action_type == ActionType.REFRESH_DBT_MODEL:
                        res = refresh_dbt_model_action(act.target)
                    else:
                        raise ValueError(f"Forbidden action type '{act.action_type.value}'")

                action_results.append(res)

            plan.status = PlanStatus.VERIFICATION_PENDING
            plan.execution_result = {
                "dry_run": self.dry_run,
                "actions_executed": len(action_results),
                "details": action_results
            }

            audit_logger.log_event(
                event_type="remediation_completed",
                incident_id=plan.incident_id,
                plan_id=plan.plan_id,
                actor="SYSTEM",
                status="EXECUTED",
                metadata=plan.execution_result
            )

            logger.info(f"Plan '{plan.plan_id}' executed successfully. Pending recovery verification.")
            return plan.execution_result

        except Exception as e:
            plan.status = PlanStatus.FAILED
            audit_logger.log_event(
                event_type="remediation_failed",
                incident_id=plan.incident_id,
                plan_id=plan.plan_id,
                actor="SYSTEM",
                status="FAILED",
                metadata={"error": str(e)}
            )
            logger.error(f"Error executing plan '{plan.plan_id}': {e}")
            raise


# Singleton instance
executor = RemediationExecutor()
