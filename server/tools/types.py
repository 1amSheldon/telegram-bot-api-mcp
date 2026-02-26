import structlog
from fastmcp import Context
from fastmcp.tools import tool
from structlog.typing import FilteringBoundLogger

from server.utils import format_type

logger: FilteringBoundLogger = structlog.get_logger()


@tool()
async def resolve_type(
        name: str,
        ctx: Context,
) -> dict:
    """Return canonical details for a Telegram Bot API type by name.

    Use this to verify field names, field types, and constraints for a Bot API
    object before generating or reviewing code.
    """

    telegram_data = ctx.lifespan_context["telegram_data"]
    name_lower = name.lower()
    actual_name = telegram_data.bot_api_types.get(name_lower)

    if not actual_name:
        return {"error": f"Type '{name}' not found"}

    type_data = telegram_data.api_data["types"][actual_name]
    await logger.ainfo("tool.resolve_type", kind="metrics")
    return format_type(type_data)


@tool()
async def list_types(
        ctx: Context,
) -> list[str]:
    """List all Telegram Bot API type names.

    Use this for discovery when the exact type name is unknown, then call
    ``resolve_type`` for detailed type information.
    """

    telegram_data = ctx.lifespan_context["telegram_data"]
    await logger.ainfo("tool.list_types", kind="metrics")
    return list(telegram_data.api_data.get("types", {}).keys())