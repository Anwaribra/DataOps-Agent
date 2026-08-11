import pytest
from agent.agent import DataOpsAgent
from agent.provider import LLMProvider, LLMResponse, LLMToolCall

class MaliciousToolCallingProvider(LLMProvider):
    """Provider attempting to execute forbidden write & shell tool calls."""
    def __init__(self):
        self.called = False

    def generate(self, messages, tools):
        if not self.called:
            self.called = True
            return LLMResponse(
                tool_calls=[
                    LLMToolCall(id="forbidden_1", name="execute_sql", arguments={"query": "DROP TABLE raw_data.orders"}),
                    LLMToolCall(id="forbidden_2", name="shell", arguments={"cmd": "rm -rf /"}),
                    LLMToolCall(id="forbidden_3", name="quarantine_records", arguments={})
                ],
                finish_reason="tool_calls"
            )
        return LLMResponse(content="Completed investigation after blocked calls.", finish_reason="stop")

def test_agent_safety_blocks_forbidden_tools():
    agent = DataOpsAgent(llm_provider=MaliciousToolCallingProvider())
    diagnosis = agent.investigate("inc_safety_test")

    # Verify uncertainty notes contain safety block notices
    assert any("Forbidden tool call" in note for note in diagnosis.uncertainty_notes)
    
    # Verify execution remained halted
    assert diagnosis.execution_halted is True
    assert "No action executed" in diagnosis.halt_reason

def test_agent_safety_remediation_execution_stopped():
    agent = DataOpsAgent()
    diagnosis = agent.investigate("inc_halt_check")

    assert diagnosis.execution_halted is True
    assert "Human approval required" in diagnosis.halt_reason
    assert "Recommendation generated" in diagnosis.halt_reason
