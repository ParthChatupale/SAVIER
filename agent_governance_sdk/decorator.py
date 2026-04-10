from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any

from .context import RunContext, current_run_context
from .listeners import register_crewai_listeners
from .transport import AsyncTransport


def monitor_crew(
    backend_url: str,
    project_name: str,
    *,
    api_key: str | None = None,
    timeout_sec: float = 2.0,
    max_queue_size: int = 1000,
    debug: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    if debug:
        logging.basicConfig(level=logging.INFO)
    transport = AsyncTransport(
        backend_url=backend_url,
        api_key=api_key,
        timeout_sec=timeout_sec,
        max_queue_size=max_queue_size,
        debug=debug,
    )
    logger = logging.getLogger("agent_governance_sdk")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = RunContext(
                run_id=str(uuid.uuid4()),
                project_name=project_name,
                backend_url=backend_url,
                debug=debug,
            )
            token = current_run_context.set(ctx)
            unregister = lambda: None

            try:
                unregister = register_crewai_listeners(ctx, transport)
                return func(*args, **kwargs)
            except Exception as exc:
                if debug:
                    logger.warning("agent_governance_sdk decorator error: %s", exc)
                raise
            finally:
                try:
                    unregister()
                except Exception as exc:
                    if debug:
                        logger.warning("agent_governance_sdk listener cleanup failed: %s", exc)
                current_run_context.reset(token)

        return wrapper

    return decorator
