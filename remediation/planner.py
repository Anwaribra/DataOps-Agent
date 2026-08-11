import logging
from typing import Dict, Any, Optional
from agent.models import AgentDiagnosis
from remediation.models import ActionType, PlanStatus, RemediationAction, RemediationPlan, RiskLevel
from remediation.validator import validator

logger = logging.getLogger("dataops.remediation.planner")

class RemediationPlanner:
    """
    Constructs structured remediation plans from AI Agent diagnosis recommendations.
    """
    def create_plan_from_diagnosis(self, diagnosis: AgentDiagnosis) -> RemediationPlan:
        logger.info(f"Formulating remediation plan for incident '{diagnosis.incident_id}'...")

        actions = []
        root_cause_lower = diagnosis.root_cause.lower()

        if "null" in root_cause_lower or "not_null" in root_cause_lower:
            actions.append(
                RemediationAction(
                    action_type=ActionType.QUARANTINE_INVALID_RECORDS,
                    target="staging.stg_orders",
                    parameters={"column_name": "customer_id", "condition": "IS NULL"},
                    reason="Isolate invalid records containing NULL customer_id from downstream marts",
                    expected_result="Quarantine table populated; 0 NULL customer_id rows remaining in stg_orders",
                    risk_level=RiskLevel.LOW,
                    idempotency_key=f"{diagnosis.incident_id}_quarantine_stg_orders"
                )
            )
            actions.append(
                RemediationAction(
                    action_type=ActionType.REFRESH_DBT_MODEL,
                    target="fct_orders",
                    parameters={},
                    reason="Rebuild downstream order fact table after quarantining corrupt records",
                    expected_result="fct_orders materializes successfully with 100% valid records",
                    risk_level=RiskLevel.MEDIUM,
                    idempotency_key=f"{diagnosis.incident_id}_refresh_fct_orders"
                )
            )
        elif "duplicate" in root_cause_lower or "unique" in root_cause_lower:
            actions.append(
                RemediationAction(
                    action_type=ActionType.QUARANTINE_INVALID_RECORDS,
                    target="staging.stg_orders",
                    parameters={"column_name": "order_id", "condition": "ROW_NUMBER() > 1"},
                    reason="Remove duplicate order primary key insertions from active staging view",
                    expected_result="Duplicate primary keys moved to quarantine table",
                    risk_level=RiskLevel.LOW,
                    idempotency_key=f"{diagnosis.incident_id}_quarantine_dup_orders"
                )
            )
            actions.append(
                RemediationAction(
                    action_type=ActionType.RERUN_DAGSTER_ASSET,
                    target="fct_orders",
                    parameters={},
                    reason="Re-execute Dagster asset pipeline for fct_orders",
                    expected_result="fct_orders completes with deduplicated primary keys",
                    risk_level=RiskLevel.MEDIUM,
                    idempotency_key=f"{diagnosis.incident_id}_rerun_dagster_fct_orders"
                )
            )
        else:
            actions.append(
                RemediationAction(
                    action_type=ActionType.REFRESH_DBT_MODEL,
                    target="stg_orders",
                    parameters={},
                    reason="Refresh staging orders dbt transformation",
                    expected_result="stg_orders view re-compiled cleanly",
                    risk_level=RiskLevel.LOW,
                    idempotency_key=f"{diagnosis.incident_id}_refresh_stg_orders"
                )
            )

        plan = RemediationPlan(
            incident_id=diagnosis.incident_id,
            reason=diagnosis.root_cause,
            actions=actions,
            expected_outcome=f"Pipeline restored to HEALTHY; {diagnosis.incident_id} resolved.",
            risk_level=RiskLevel.MEDIUM,
            status=PlanStatus.PENDING_APPROVAL
        )

        # Validate plan
        validation = validator.validate_plan(plan)
        if not validation["valid"]:
            logger.error(f"Plan validation failed: {validation['reason']}")
            plan.status = PlanStatus.FAILED
            plan.reason = f"Plan validation error: {validation['reason']}"

        return plan


# Singleton instance
planner = RemediationPlanner()
