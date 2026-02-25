from fastmcp import Context
from fastmcp.tools import tool

from server.utils import format_type


@tool()
async def resolve_type(
        name: str,
        ctx: Context,
) -> dict:
    """Resolve a Telegram Bot API type by name."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    name_lower = name.lower()
    actual_name = telegram_data.bot_api_types.get(name_lower)

    if not actual_name:
        return {"error": f"Type '{name}' not found"}

    type_data = telegram_data.api_data["types"][actual_name]
    return format_type(type_data)


@tool()
async def list_types(
        ctx: Context,
) -> list[str]:
    """List all available Telegram Bot API types."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    return list(telegram_data.api_data.get("types", {}).keys())