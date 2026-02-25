from fastmcp import Context
from fastmcp.tools import tool

from server.utils import format_method


@tool()
async def resolve_method(
        name: str,
        ctx: Context,
) -> dict:
    """Resolve a Telegram Bot API method by name."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    name_key = name.lower().replace("_", "")
    if name_key not in telegram_data["bot_api_methods"]:
        return {"error": f"Method '{name}' not found"}

    actual_name = telegram_data["bot_api_methods"][name_key]
    method_info = telegram_data.api_data["methods"][actual_name]
    return format_method(method_info)


@tool()
async def list_methods(
        ctx: Context,
) -> list[str]:
    """List all available Telegram Bot API methods."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    return list(telegram_data.api_data.get("methods", {}).keys())