import pytest
from failure_injection.scenarios import set_active_scenario
from agent.agent import DataOpsAgent
from agent.provider import FakeLLMProvider

def test_agent_investigate_null_customer_id_scenario():
    set_active_scenario("null_customer_id")
    agent = DataOpsAgent(llm_provider=FakeLLMProvider(scenario="null_customer_id"))
    diagnosis = agent.investigate("inc_null_cust_001")

    assert diagnosis.incident_id == "inc_null_cust_001"
    assert diagnosis.severity == "HIGH"
    assert diagnosis.confidence >= 0.90
    assert "NULL customer_id" in diagnosis.root_cause
    assert len(diagnosis.observed_evidence) > 0
    assert len(diagnosis.recommended_actions) > 0
    assert diagnosis.execution_halted is True
    set_active_scenario(None)

def test_agent_investigate_duplicate_order_id_scenario():
    set_active_scenario("duplicate_order_id")
    agent = DataOpsAgent(llm_provider=FakeLLMProvider(scenario="duplicate_order_id"))
    diagnosis = agent.investigate("inc_dup_order_002")

    assert diagnosis.incident_id == "inc_dup_order_002"
    assert diagnosis.severity == "HIGH"
    assert "duplicate" in diagnosis.root_cause.lower()
    assert diagnosis.execution_halted is True
    set_active_scenario(None)

def test_agent_investigate_healthy_pipeline():
    set_active_scenario(None)
    agent = DataOpsAgent(llm_provider=FakeLLMProvider(scenario="healthy"))
    diagnosis = agent.investigate("inc_healthy_000")

    assert diagnosis.incident_id == "inc_healthy_000"
    assert diagnosis.status == "DIAGNOSED"
    assert diagnosis.execution_halted is True
