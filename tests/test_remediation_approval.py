import pytest
from remediation.approval import approval_service
from remediation.models import ActionType, PlanStatus, RemediationAction, RemediationPlan

def test_approve_valid_plan():
    plan = RemediationPlan(
        incident_id="inc_appr_01",
        reason="Test plan",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")],
        expected_outcome="test outcome",
        status=PlanStatus.PENDING_APPROVAL
    )
    approval_service.register_plan(plan)

    approved_plan = approval_service.approve_plan(plan.plan_id, approver="OPERATOR_BOB")
    assert approved_plan.status == PlanStatus.APPROVED
    assert approved_plan.approved_by == "OPERATOR_BOB"
    assert approved_plan.approval_id is not None
    assert approved_plan.expires_at is not None

def test_prevent_agent_self_approval():
    plan = RemediationPlan(
        incident_id="inc_self_appr",
        reason="Test plan",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")],
        expected_outcome="test outcome",
        status=PlanStatus.PENDING_APPROVAL
    )
    approval_service.register_plan(plan)

    with pytest.raises(ValueError, match="AI Agent is forbidden from approving"):
        approval_service.approve_plan(plan.plan_id, approver="DATAOPS_AGENT")

def test_reject_plan():
    plan = RemediationPlan(
        incident_id="inc_rej_01",
        reason="Test plan",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")],
        expected_outcome="test outcome",
        status=PlanStatus.PENDING_APPROVAL
    )
    approval_service.register_plan(plan)

    rejected = approval_service.reject_plan(plan.plan_id, approver="OPERATOR_ALICE", reason="Risk too high")
    assert rejected.status == PlanStatus.REJECTED
