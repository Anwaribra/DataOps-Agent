import os
import pytest
from unittest.mock import MagicMock, patch
from agent.provider import OpenRouterLLMProvider, FakeLLMProvider, get_llm_provider
from agent.agent import DataOpsAgent

def test_openrouter_provider_fallback_without_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    provider = OpenRouterLLMProvider(api_key=None)
    
    # Should fall back to FakeLLMProvider when key is missing
    resp = provider.generate([{"role": "user", "content": "investigate"}], [])
    assert resp is not None
    assert len(resp.tool_calls) > 0 or resp.content is not None

def test_openrouter_provider_mocked_generate(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-mock-key-12345")
    provider = OpenRouterLLMProvider(api_key="sk-or-v1-mock-key-12345", model="meta-llama/llama-3.3-70b-instruct:free")

    mock_choice = MagicMock()
    mock_choice.finish_reason = "tool_calls"
    mock_msg = MagicMock()
    mock_msg.content = "Investigating pipeline..."
    
    mock_tc = MagicMock()
    mock_tc.id = "call_openrouter_01"
    mock_tc.name = "get_diagnosis"
    mock_tc.arguments = '{"incident_id": "inc_b91673ef"}'
    mock_tc.function.name = "get_diagnosis"
    mock_tc.function.arguments = '{"incident_id": "inc_b91673ef"}'
    mock_msg.tool_calls = [mock_tc]
    mock_choice.message = mock_msg

    mock_openai_resp = MagicMock()
    mock_openai_resp.choices = [mock_choice]

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_resp
        mock_openai_cls.return_value = mock_client

        resp = provider.generate([{"role": "user", "content": "test"}], [{"name": "get_diagnosis", "description": "test"}])
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].name == "get_diagnosis"

def test_get_llm_provider_openrouter(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-mock")
    
    provider = get_llm_provider()
    assert isinstance(provider, OpenRouterLLMProvider)

def test_agent_tool_conversion_with_openrouter(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-mock")

    tc1 = MagicMock()
    tc1.id = "tc_1"
    tc1.name = "get_diagnosis"
    tc1.arguments = {}

    mock_provider = MagicMock()
    mock_provider.generate.side_effect = [
        MagicMock(
            content=None,
            tool_calls=[tc1],
            finish_reason="tool_calls"
        ),
        MagicMock(
            content="Diagnosis complete.",
            tool_calls=[],
            finish_reason="stop"
        )
    ]

    agent = DataOpsAgent(llm_provider=mock_provider)
    diagnosis = agent.investigate("inc_openrouter_test")

    assert diagnosis.incident_id == "inc_openrouter_test"
    assert mock_provider.generate.call_count == 2
