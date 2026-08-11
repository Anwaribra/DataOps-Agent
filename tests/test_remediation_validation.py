import pytest
from remediation.models import ActionType, RemediationAction, RemediationPlan
from remediation.validator import validator

def test_valid_plan_validation():
    plan = RemediationPlan(
        incident_id="inc_val_01",
        reason="Test",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="fct_orders", reason="test")],
        expected_outcome="test outcome"
    )
    res = validator.validate_plan(plan)
    assert res["valid"] is True

def test_invalid_target_validation():
    plan = RemediationPlan(
        incident_id="inc_val_02",
        reason="Test",
        actions=[RemediationAction(action_type=ActionType.REFRESH_DBT_MODEL, target="unapproved_secret_table", reason="test")],
        expected_outcome="test outcome"
    )
    res = validator.validate_plan(plan)
    assert res["valid"] is False
    assert "not in approved allowlist" in res["reason"]
