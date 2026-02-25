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

    actual_name = None
    for method_name in telegram_data.api_data.get("methods", {}).keys():
        if method_name.lower().replace("_", "") == name_key:
            actual_name = method_name
            break

    if not actual_name:
        return {"error": f"Method '{name}' not found"}

    method = telegram_data.api_data["methods"][actual_name]
    return format_method(method)


@tool()
async def list_methods(
        ctx: Context,
) -> list[str]:
    """List all available Telegram Bot API methods."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    return list(telegram_data.api_data.get("methods", {}).keys())