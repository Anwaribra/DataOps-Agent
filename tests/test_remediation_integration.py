import pytest
from failure_injection.scenarios import set_active_scenario
from agent.agent import DataOpsAgent
from agent.provider import FakeLLMProvider
from diagnosis.engine import DiagnosisEngine, IncidentStatus
from remediation.approval import approval_service
from remediation.executor import executor
from remediation.planner import planner
from remediation.verifier import verifier

def test_full_closed_loop_dataops_remediation_lifecycle():
    # 1. Inject Failure Scenario (NULL customer_id)
    set_active_scenario("null_customer_id")

    # 2. Detect & Create Incident
    diag_engine = DiagnosisEngine()
    incident = diag_engine.diagnose_active_pipeline()
    assert incident.status == IncidentStatus.DIAGNOSED
    assert incident.severity.value == "high"

    # 3. AI DataOps Agent Investigation
    agent = DataOpsAgent(llm_provider=FakeLLMProvider(scenario="null_customer_id"))
    agent_diagnosis = agent.investigate(incident.incident_id)
    assert agent_diagnosis.execution_halted is True

    # 4. Agent Proposes Remediation Plan
    plan = planner.create_plan_from_diagnosis(agent_diagnosis)
    approval_service.register_plan(plan)
    assert plan.status.value == "PENDING_APPROVAL"
    assert len(plan.actions) >= 2

    # 5. Human Operator Approves Plan
    approved_plan = approval_service.approve_plan(plan.plan_id, approver="OPERATOR_JANE")
    assert approved_plan.status.value == "APPROVED"
    assert approved_plan.approved_by == "OPERATOR_JANE"

    # 6. Controlled Executor Executes Plan
    exec_result = executor.execute_plan(approved_plan)
    assert exec_result["actions_executed"] == len(plan.actions)

    # 7. Recovery Verifier Audits Pipeline Health
    verif_result = verifier.verify_recovery(approved_plan)
    assert verif_result.status == "PASSED"
    assert approved_plan.status.value == "VERIFIED"

    # 8. Incident Status updated to RESOLVED
    assert incident.status == IncidentStatus.RESOLVED

    # Clean up failure scenario
    set_active_scenario(None)
