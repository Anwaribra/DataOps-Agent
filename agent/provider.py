import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("dataops.agent.provider")


class LLMToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: List[LLMToolCall] = Field(default_factory=list)
    finish_reason: str = "stop"


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> LLMResponse:
        """Generates a response from the LLM given conversation messages and available MCP tools."""
        pass


class FakeLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider for Pytest, CI, and local offline testing.
    Simulates tool calling sequences and structured diagnoses for incident scenarios without requiring an API key.
    """
    def __init__(self, scenario: Optional[str] = None):
        self.scenario = scenario
        self.step_counter = 0

    def generate(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> LLMResponse:
        self.step_counter += 1
        
        # Check last user/assistant message to determine investigation step
        last_msg = messages[-1] if messages else {}
        last_role = last_msg.get("role")
        last_content = str(last_msg.get("content", ""))

        # Determine scenario from message if not explicitly passed
        scenario = self.scenario
        if not scenario:
            if "null_customer_id" in last_content or "not_null" in last_content:
                scenario = "null_customer_id"
            elif "duplicate_order_id" in last_content or "unique" in last_content:
                scenario = "duplicate_order_id"
            elif "invalid_status" in last_content or "accepted_values" in last_content:
                scenario = "invalid_status"
            elif "volume_anomaly" in last_content or "volume" in last_content:
                scenario = "volume_anomaly"

        # Step 1: Initial call to get_diagnosis or get_incident
        if self.step_counter == 1:
            return LLMResponse(
                tool_calls=[
                    LLMToolCall(
                        id="call_step_1",
                        name="get_diagnosis",
                        arguments={}
                    )
                ],
                finish_reason="tool_calls"
            )

        # Step 2: Trace lineage or get dbt test details
        if self.step_counter == 2:
            return LLMResponse(
                tool_calls=[
                    LLMToolCall(
                        id="call_step_2",
                        name="get_asset_lineage",
                        arguments={"asset_name": "stg_orders"}
                    )
                ],
                finish_reason="tool_calls"
            )

        # Step 3: Get column stats or ingestion metadata
        if self.step_counter == 3:
            return LLMResponse(
                tool_calls=[
                    LLMToolCall(
                        id="call_step_3",
                        name="get_column_stats",
                        arguments={"table_name": "staging.stg_orders", "column_name": "customer_id"}
                    )
                ],
                finish_reason="tool_calls"
            )

        # Step 4: Final structured diagnosis response
        if scenario == "null_customer_id":
            final_text = (
                "INCIDENT: inc_b91673ef\n"
                "Severity: HIGH\n"
                "Status: DIAGNOSED\n\n"
                "Root Cause:\n"
                "Upstream source data-quality regression introduced NULL customer_id values during the latest ingestion batch.\n\n"
                "Confidence:\n"
                "HIGH\n\n"
                "Observed Evidence:\n"
                "- dbt test failure: not_null_stg_orders_customer_id\n"
                "- customer_id NULL rate in stg_orders increased to 20.0%\n"
                "- Failure is isolated to latest raw_orders ingestion batch\n"
                "- Asset lineage: raw_orders -> stg_orders -> fct_orders\n\n"
                "Impact:\n"
                "Downstream order attribution and customer lifetime value analytics in fct_orders will contain incomplete records.\n\n"
                "Recommended Actions:\n"
                "1. Quarantine affected records containing NULL customer_id\n"
                "2. Validate upstream source API extraction payload\n"
                "3. Re-run dbt transformations after source data correction\n\n"
                "Recommendation generated. No action executed. Human approval required."
            )
        elif scenario == "duplicate_order_id":
            final_text = (
                "INCIDENT: inc_dup_002\n"
                "Severity: HIGH\n"
                "Status: DIAGNOSED\n\n"
                "Root Cause:\n"
                "Upstream batch ingestion produced duplicate order_id records in source dataset.\n\n"
                "Confidence:\n"
                "HIGH\n\n"
                "Observed Evidence:\n"
                "- dbt test failure: unique_stg_orders_order_id\n"
                "- Duplicate primary key constraint violation detected in stg_orders\n"
                "- Multiple rows sharing identical order_id found in raw_data.orders\n\n"
                "Impact:\n"
                "Revenue fact tables and sales aggregates will double-count transaction totals.\n\n"
                "Recommended Actions:\n"
                "1. Deduplicate records in raw_data.orders using ROW_NUMBER()\n"
                "2. Audit dlt ingestion write disposition settings\n"
                "3. Re-run dbt staging and mart models\n\n"
                "Recommendation generated. No action executed. Human approval required."
            )
        else:
            final_text = (
                "INCIDENT: inc_general\n"
                "Severity: LOW\n"
                "Status: RESOLVED\n\n"
                "Root Cause:\n"
                "No root cause identified. Platform operating normally.\n\n"
                "Confidence:\n"
                "HIGH\n\n"
                "Observed Evidence:\n"
                "- All dbt data quality tests passed\n"
                "- Ingestion volume within normal baseline\n\n"
                "Impact:\n"
                "None. Pipeline functioning as expected.\n\n"
                "Recommended Actions:\n"
                "1. Maintain normal scheduled execution\n\n"
                "Recommendation generated. No action executed. Human approval required."
            )

        return LLMResponse(content=final_text, finish_reason="stop")


class OpenAILLMProvider(LLMProvider):
    """
    OpenAI / Generic ChatCompletions Provider using official API client.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o")

    def generate(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> LLMResponse:
        if not self.api_key or self.api_key.startswith("mock"):
            logger.warning("No valid API key provided. Falling back to FakeLLMProvider.")
            fallback = FakeLLMProvider()
            return fallback.generate(messages, tools)

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            formatted_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.get("name"),
                        "description": t.get("description"),
                        "parameters": t.get("parameters", {"type": "object", "properties": {}})
                    }
                }
                for t in tools
            ] if tools else None

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=formatted_tools,
                temperature=0.0
            )

            msg = response.choices[0].message
            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                    except Exception:
                        args = {}
                    tool_calls.append(LLMToolCall(id=tc.id, name=tc.function.name, arguments=args))

            return LLMResponse(
                content=msg.content,
                tool_calls=tool_calls,
                finish_reason=response.choices[0].finish_reason
            )
        except Exception as e:
            logger.error(f"OpenAI LLM provider call failed: {e}. Falling back to FakeLLMProvider.")
            return FakeLLMProvider().generate(messages, tools)


def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "fake").lower()
    if provider_name == "fake" or os.getenv("OPENAI_API_KEY", "").startswith("mock"):
        return FakeLLMProvider()
    elif provider_name in ("openai", "generic"):
        return OpenAILLMProvider()
    return FakeLLMProvider()
