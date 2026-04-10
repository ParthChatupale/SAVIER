from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def normalize_payload(
    *,
    run_id: str,
    agent_name: Any = "",
    task: Any = "",
    thought: Any = "",
    tool_name: Any = "",
    tool_input: Any = "",
    tokens_used: Any = 0,
    execution_time_sec: Any = 0.0,
) -> dict[str, Any]:
    return {
        "run_id": _to_text(run_id),
        "agent_name": _to_text(agent_name),
        "timestamp": datetime.now(UTC).isoformat(),
        "task": _to_text(task),
        "thought": _to_text(thought),
        "tool_name": _to_text(tool_name),
        "tool_input": _truncate(_to_text(tool_input)),
        "tokens_used": _to_int(tokens_used),
        "execution_time_sec": _to_float(execution_time_sec),
    }


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    for attr in ("description", "name", "role", "content", "raw"):
        candidate = getattr(value, attr, None)
        if isinstance(candidate, str) and candidate:
            return candidate
    return str(value)


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return 0.0


def _truncate(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."
