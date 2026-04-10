from __future__ import annotations

import importlib
import time
from collections.abc import Callable
from typing import Any

from .context import LLMCallState, RunContext, ToolState
from .models import normalize_payload
from .transport import AsyncTransport


def register_crewai_listeners(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[], None]:
    bus = _load_event_bus()
    if bus is None:
        if ctx.debug:
            import logging
            logging.getLogger("agent_governance_sdk").warning(
                "CrewAI event bus not found; telemetry disabled."
            )
        return lambda: None

    scope = getattr(bus, "scoped_handlers", None)
    if not callable(scope):
        if ctx.debug:
            import logging
            logging.getLogger("agent_governance_sdk").warning(
                "CrewAI event bus does not support scoped handlers; telemetry disabled."
            )
        return lambda: None

    if ctx.debug:
        import logging
        logging.getLogger("agent_governance_sdk").info(
            "CrewAI event bus found; registering handlers."
        )

    manager = scope()
    manager.__enter__()

    registered = _attach_handlers(bus, ctx, transport)
    if ctx.debug and registered == 0:
        import logging
        logging.getLogger("agent_governance_sdk").warning(
            "No CrewAI event handlers registered; check SDK compatibility."
        )
    elif ctx.debug:
        import logging
        logging.getLogger("agent_governance_sdk").info(
            "CrewAI handlers registered: %s", registered
        )

    def unregister() -> None:
        try:
            manager.__exit__(None, None, None)
        except Exception:
            return

    return unregister


def _load_event_bus() -> Any | None:
    candidates = (
        "crewai.events.event_bus.crewai_event_bus",
    )
    for dotted_path in candidates:
        module_name, attr_name = dotted_path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        bus = getattr(module, attr_name, None)
        if bus is not None:
            return bus
    return None


def _attach_handlers(bus: Any, ctx: RunContext, transport: AsyncTransport) -> int:
    registered = 0
    for event_name in ("TaskStartedEvent", "TaskExecutionStartedEvent"):
        registered += int(_safe_register(bus, event_name, _build_task_started_handler(ctx, transport)))

    for event_name in ("AgentExecutionStartedEvent", "AgentStartedEvent"):
        registered += int(_safe_register(bus, event_name, _build_agent_started_handler(ctx, transport)))

    registered += int(_safe_register(bus, "ToolUsageStartedEvent", _build_tool_started_handler(ctx, transport)))
    registered += int(_safe_register(bus, "ToolUsageFinishedEvent", _build_tool_finished_handler(ctx, transport)))
    registered += int(_safe_register(bus, "LLMCallStartedEvent", _build_llm_started_handler(ctx, transport)))
    registered += int(_safe_register(bus, "LLMCallCompletedEvent", _build_llm_completed_handler(ctx, transport)))
    registered += int(_safe_register(bus, "AgentExecutionCompletedEvent", _build_agent_completed_handler(ctx, transport)))
    return registered


def _safe_register(bus: Any, event_name: str, handler: Callable[[Any, Any], None]) -> bool:
    register = getattr(bus, "on", None)
    if not callable(register):
        return False

    event_type = _load_event_type(event_name)
    if event_type is None:
        return False

    try:
        register(event_type)(handler)
    except Exception:
        return False
    return True


def _load_event_type(event_name: str) -> Any | None:
    modules = (
        "crewai.events.types.agent_events",
        "crewai.events.types.task_events",
        "crewai.events.types.tool_usage_events",
        "crewai.events.types.llm_events",
        "crewai.events.types.reasoning_events",
        "crewai.events.types.logging_events",
        "crewai.events.types.crew_events",
    )
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        event_type = getattr(module, event_name, None)
        if event_type is not None:
            return event_type
    return None


def _build_task_started_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        ctx.update_task(_extract_first(event, "task", "task_name", "description", "name"))
        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name="task_started",
            tool_input="",
            tokens_used=0,
            execution_time_sec=0.0,
        )

    return handler


def _build_agent_started_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        ctx.update_agent(_extract_first(event, "agent", "agent_role", "name", "role"))
        ctx.update_task(_extract_first(event, "task", "task_name", "description", "name"))
        ctx.update_thought(_extract_first(event, "thought", "message", "content"))
        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name="agent_execution_started",
            tool_input="",
            tokens_used=0,
            execution_time_sec=0.0,
        )

    return handler


def _build_tool_started_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        correlation_id = _event_correlation_id(event, ctx)
        tool_name = _coalesce(
            _extract_first(event, "tool_name", "name"),
            _extract_nested(event, "tool", "name"),
        )
        tool_input = _coalesce(
            _extract_first(event, "tool_input", "tool_args", "input", "arguments"),
            _extract_nested(event, "tool", "input"),
        )
        ctx.active_tools[correlation_id] = ToolState(
            correlation_id=correlation_id,
            started_at=time.perf_counter(),
            agent_name=_coalesce(
                _extract_first(event, "agent_name", "agent_role", "agent_key"),
                _extract_nested(event, "agent", "name"),
                ctx.current_agent,
            ),
            task=_coalesce(
                _extract_first(event, "task", "task_name"),
                _extract_nested(event, "task", "description"),
                ctx.current_task,
            ),
            thought=_coalesce(
                _extract_first(event, "thought"),
                ctx.last_thought,
            ),
            tool_name=tool_name,
            tool_input=tool_input,
        )
        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name=tool_name or "tool_usage_started",
            tool_input=tool_input,
            tokens_used=0,
            execution_time_sec=0.0,
        )

    return handler


def _build_tool_finished_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        correlation_id = _event_correlation_id(event, ctx)
        state = ctx.active_tools.pop(correlation_id, None)
        if state is None:
            state = ToolState(
                correlation_id=correlation_id,
                started_at=time.perf_counter(),
            )

        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name=_coalesce(
                _extract_first(event, "tool_name", "name"),
                _extract_nested(event, "tool", "name"),
                state.tool_name,
            ),
            tool_input=_coalesce(
                _extract_first(event, "tool_input", "tool_args", "input", "arguments"),
                _extract_nested(event, "tool", "input"),
                state.tool_input,
            ),
            tokens_used=_coalesce(
                _extract_token_usage(event),
                ctx.last_token_usage,
            ),
            execution_time_sec=time.perf_counter() - state.started_at,
        )

    return handler


def _build_llm_started_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        call_id = _coalesce(
            _extract_first(event, "call_id", "id"),
            "",
        )
        if not call_id:
            return
        ctx.active_llm_calls[call_id] = LLMCallState(
            call_id=call_id,
            started_at=time.perf_counter(),
            agent_name=_coalesce(
                _extract_first(event, "agent_name", "agent_role", "agent_key"),
                _extract_nested(event, "agent", "name"),
                ctx.current_agent,
            ),
            task=_coalesce(
                _extract_first(event, "task", "task_name"),
                _extract_nested(event, "task", "description"),
                ctx.current_task,
            ),
            thought=_coalesce(
                _extract_first(event, "thought"),
                ctx.last_thought,
            ),
            model=_coalesce(_extract_first(event, "model"), ""),
            prompt=_coalesce(_extract_first(event, "messages"), ""),
        )
        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name=_coalesce(_extract_first(event, "model"), "llm_call_started"),
            tool_input=_coalesce(_extract_first(event, "messages"), ""),
            tokens_used=0,
            execution_time_sec=0.0,
        )

    return handler


def _build_llm_completed_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        tokens_used = _extract_token_usage(event)
        ctx.last_token_usage = tokens_used
        ctx.update_thought(_extract_first(event, "thought", "response", "content"))

        call_id = _coalesce(
            _extract_first(event, "call_id", "id"),
            "",
        )
        state = ctx.active_llm_calls.pop(call_id, None)
        if state is None:
            state = LLMCallState(
                call_id=call_id or "llm_call",
                started_at=time.perf_counter(),
                agent_name=ctx.current_agent,
                task=ctx.current_task,
                thought=ctx.last_thought,
            )

        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name=_coalesce(state.model, "llm_call"),
            tool_input=_coalesce(state.prompt, ""),
            tokens_used=tokens_used,
            execution_time_sec=time.perf_counter() - state.started_at,
        )

    return handler


def _build_agent_completed_handler(
    ctx: RunContext,
    transport: AsyncTransport,
) -> Callable[[Any, Any], None]:
    def handler(_source: Any, event: Any) -> None:
        if ctx.active_tools:
            return

        tokens_used = _coalesce(
            _extract_token_usage(event),
            ctx.last_token_usage,
        )
        execution_time = _coalesce(
            _extract_first(event, "execution_time_sec", "execution_time", "duration"),
            0.0,
        )
        _emit_payload(
            ctx,
            event=event,
            transport=transport,
            tool_name="agent_execution_completed",
            tool_input="",
            tokens_used=tokens_used,
            execution_time_sec=execution_time,
        )

    return handler


def _emit_payload(
    ctx: RunContext,
    *,
    event: Any,
    transport: AsyncTransport,
    tool_name: Any,
    tool_input: Any,
    tokens_used: Any,
    execution_time_sec: Any,
) -> None:
    payload = normalize_payload(
        run_id=ctx.run_id,
        agent_name=_coalesce(
            _extract_first(event, "agent_name", "agent_role", "agent_key"),
            _extract_nested(event, "agent", "name"),
            ctx.current_agent,
        ),
        task=_coalesce(
            _extract_first(event, "task", "task_name"),
            _extract_nested(event, "task", "description"),
            ctx.current_task,
        ),
        thought=_coalesce(
            _extract_first(event, "thought", "output", "response", "content"),
            ctx.last_thought,
        ),
        tool_name=tool_name,
        tool_input=tool_input,
        tokens_used=tokens_used,
        execution_time_sec=execution_time_sec,
    )
    transport.enqueue(payload)


def _extract_token_usage(event: Any) -> int:
    usage = _extract_first(event, "tokens_used", "token_usage", "usage")
    if usage is None:
        return 0
    if isinstance(usage, int):
        return usage
    if isinstance(usage, dict):
        for key in ("total_tokens", "tokens", "total"):
            value = usage.get(key)
            if isinstance(value, int):
                return value
        return 0
    for attr in ("total_tokens", "tokens", "total"):
        value = getattr(usage, attr, None)
        if isinstance(value, int):
            return value
    try:
        return int(usage)
    except (TypeError, ValueError):
        return 0


def _extract_first(obj: Any, *names: str) -> Any:
    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return value
    return None


def _extract_nested(obj: Any, parent_name: str, child_name: str) -> Any:
    parent = getattr(obj, parent_name, None)
    if parent is None:
        return None
    return getattr(parent, child_name, None)


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return ""


def _event_correlation_id(event: Any, ctx: RunContext) -> str:
    for name in ("correlation_id", "tool_call_id", "call_id", "id"):
        value = getattr(event, name, None)
        if value not in (None, ""):
            return str(value)

    tool_name = _coalesce(
        _extract_first(event, "tool_name", "name"),
        _extract_nested(event, "tool", "name"),
        "tool",
    )
    agent_name = _coalesce(
        _extract_first(event, "agent_name"),
        _extract_nested(event, "agent", "name"),
        ctx.current_agent,
        "agent",
    )
    return f"{agent_name}:{tool_name}"
