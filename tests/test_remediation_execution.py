import pytest
from remediation.approval import approval_service
from remediation.executor import executor
from remediation.models import ActionType, PlanStatus, RemediationAction, RemediationPlan

def test_execution_requires_approval():
    plan = RemediationPlan(
        incident_id="inc_exec_01",
        reason="Test",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")],
        expected_outcome="test outcome",
        status=PlanStatus.PENDING_APPROVAL
    )
    approval_service.register_plan(plan)

    with pytest.raises(ValueError, match="unapproved or approval TTL has expired"):
        executor.execute_plan(plan)

def test_approved_plan_execution():
    plan = RemediationPlan(
        incident_id="inc_exec_02",
        reason="Test",
        actions=[
            RemediationAction(action_type=ActionType.QUARANTINE_INVALID_RECORDS, target="staging.stg_orders", parameters={"column_name": "customer_id"}, reason="test"),
            RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")
        ],
        expected_outcome="test outcome",
        status=PlanStatus.PENDING_APPROVAL
    )
    approval_service.register_plan(plan)
    approval_service.approve_plan(plan.plan_id, approver="OPERATOR_BOB")

    res = executor.execute_plan(plan)
    assert res["actions_executed"] == 2
    assert plan.status == PlanStatus.VERIFICATION_PENDING
