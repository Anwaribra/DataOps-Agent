from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TraceStep(BaseModel):
    step_number: int
    tool_name: str
    reason: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result_summary: str
    extracted_evidence: List[str] = Field(default_factory=list)


class InvestigationTrace:
    """
    Structured execution tracing for DataOps Agent investigations.
    Omits model internal chain-of-thought, recording auditable tool calls and evidence summaries.
    """
    def __init__(self):
        self.steps: List[TraceStep] = []

    def add_step(
        self,
        step_number: int,
        tool_name: str,
        reason: str,
        arguments: Dict[str, Any],
        result_summary: str,
        extracted_evidence: Optional[List[str]] = None
    ) -> TraceStep:
        step = TraceStep(
            step_number=step_number,
            tool_name=tool_name,
            reason=reason,
            arguments=arguments,
            result_summary=result_summary,
            extracted_evidence=extracted_evidence or []
        )
        self.steps.append(step)
        return step

    def to_list(self) -> List[Dict[str, Any]]:
        return [step.model_dump() for step in self.steps]
