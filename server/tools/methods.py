import structlog
from fastmcp import Context
from fastmcp.tools import tool
from structlog.typing import FilteringBoundLogger

from server.utils import format_method

logger: FilteringBoundLogger = structlog.get_logger()


@tool()
async def resolve_method(
        name: str,
        ctx: Context,
) -> dict:
    """Return canonical details for a Telegram Bot API method by name.

    Use this to verify method parameters, return type, and field semantics against
    the official Bot API spec before giving implementation advice.
    """

    telegram_data = ctx.lifespan_context["telegram_data"]
    name_key = name.lower().replace("_", "")
    if name_key not in telegram_data["bot_api_methods"]:
        return {"error": f"Method '{name}' not found"}

    actual_name = telegram_data["bot_api_methods"][name_key]
    method_info = telegram_data.api_data["methods"][actual_name]
    await logger.ainfo("tool.resolve_method", kind="metrics")
    return format_method(method_info)


@tool()
async def list_methods(
        ctx: Context,
) -> list[str]:
    """List all Telegram Bot API method names.

    Use this for discovery when the exact method is unknown, then call
    ``resolve_method`` for full method details.
    """

    telegram_data = ctx.lifespan_context["telegram_data"]
    await logger.ainfo("tool.list_methods", kind="metrics")
    return list(telegram_data.api_data.get("methods", {}).keys())