from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

import structlog
from structlog.typing import FilteringBoundLogger


logger: FilteringBoundLogger = structlog.get_logger()


def metrics(event_name: str) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for consistent asynchronous tool telemetry."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            await logger.ainfo(event_name, kind="metrics")
            return await func(*args, **kwargs)

        return wrapper

    return decorator
