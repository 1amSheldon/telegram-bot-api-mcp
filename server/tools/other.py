from fastmcp import Context
from fastmcp.tools import tool


@tool()
async def get_version(
        ctx: Context,
) -> str:
    """Get current Telegram Bot API version."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    return telegram_data.version


@tool()
async def get_changelog_link(
        ctx: Context,
) -> str:
    """Get link to the most recent changelog."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    return telegram_data.changelog_link