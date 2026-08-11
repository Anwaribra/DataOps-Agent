import pytest
from agent.agent import DataOpsAgent
from agent.provider import FakeLLMProvider

def test_agent_max_tool_calls_budget():
    agent = DataOpsAgent(llm_provider=FakeLLMProvider(), max_tool_calls=2, max_steps=5)
    diagnosis = agent.investigate("inc_budget_test")
    assert len(diagnosis.investigation_trace) <= 2

def test_agent_max_steps_budget():
    agent = DataOpsAgent(llm_provider=FakeLLMProvider(), max_tool_calls=10, max_steps=1)
    diagnosis = agent.investigate("inc_step_test")
    assert len(diagnosis.investigation_trace) <= 1

def test_agent_trace_recording():
    agent = DataOpsAgent(llm_provider=FakeLLMProvider())
    diagnosis = agent.investigate("inc_trace_test")
    assert len(diagnosis.investigation_trace) > 0
    first_step = diagnosis.investigation_trace[0]
    assert "tool_name" in first_step
    assert "result_summary" in first_step
