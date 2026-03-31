import os
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

import structlog
from structlog.typing import FilteringBoundLogger


logger: FilteringBoundLogger = structlog.get_logger()
METRICS_LOG_ENABLED = os.getenv("TELEGRAM_MCP_METRICS_LOG_ENABLED", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def metrics(event_name: str) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for consistent asynchronous tool telemetry."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if METRICS_LOG_ENABLED:
                await logger.ainfo(event_name, kind="metrics")
            return await func(*args, **kwargs)

        return wrapper

    return decorator
