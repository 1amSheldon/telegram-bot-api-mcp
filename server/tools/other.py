import structlog
from fastmcp import Context
from fastmcp.tools import tool
from structlog.typing import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()


@tool()
async def get_version(
        ctx: Context,
) -> str:
    """Get current Telegram Bot API version."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    await logger.ainfo("tool.get_version", kind="metrics")
    return telegram_data.version


@tool()
async def get_changelog_link(
        ctx: Context,
) -> str:
    """Get link to the most recent changelog."""

    telegram_data = ctx.lifespan_context["telegram_data"]
    return telegram_data.changelog_link