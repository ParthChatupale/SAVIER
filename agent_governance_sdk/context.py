from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any


current_run_context: ContextVar["RunContext | None"] = ContextVar(
    "agent_governance_current_run_context",
    default=None,
)


@dataclass(slots=True)
class ToolState:
    correlation_id: str
    started_at: float
    agent_name: str = ""
    task: str = ""
    thought: str = ""
    tool_name: str = ""
    tool_input: str = ""


@dataclass(slots=True)
class LLMCallState:
    call_id: str
    started_at: float
    agent_name: str = ""
    task: str = ""
    thought: str = ""
    model: str = ""
    prompt: str = ""


@dataclass(slots=True)
class RunContext:
    run_id: str
    project_name: str
    backend_url: str
    debug: bool = False
    current_task: str = ""
    current_agent: str = ""
    last_thought: str = ""
    last_token_usage: int = 0
    active_tools: dict[str, ToolState] = field(default_factory=dict)
    active_llm_calls: dict[str, LLMCallState] = field(default_factory=dict)

    def update_task(self, value: Any) -> None:
        text = _stringify(value)
        if text:
            self.current_task = text

    def update_agent(self, value: Any) -> None:
        text = _stringify(value)
        if text:
            self.current_agent = text

    def update_thought(self, value: Any) -> None:
        text = _stringify(value)
        if text:
            self.last_thought = text


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    for attr in ("description", "name", "role", "content", "raw"):
        candidate = getattr(value, attr, None)
        if isinstance(candidate, str) and candidate:
            return candidate
    return str(value)
