import pytest
from remediation.approval import approval_service
from remediation.executor import executor
from remediation.models import ActionType, PlanStatus, RemediationAction, RemediationPlan
from remediation.verifier import verifier

def test_recovery_verification_success():
    plan = RemediationPlan(
        incident_id="inc_verif_01",
        reason="Test",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")],
        expected_outcome="test outcome",
        status=PlanStatus.PENDING_APPROVAL
    )
    approval_service.register_plan(plan)
    approval_service.approve_plan(plan.plan_id, approver="OPERATOR_ALICE")
    executor.execute_plan(plan)

    res = verifier.verify_recovery(plan)
    assert res.status == "PASSED"
    assert len(res.checks) >= 3
    assert plan.status == PlanStatus.VERIFIED
