import structlog
from fastmcp import Context
from fastmcp.tools import tool
from structlog.typing import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()


@tool()
async def get_version(
        ctx: Context,
) -> str:
    """Return the current Telegram Bot API version.

    Use this when version-specific behavior may affect implementation guidance.
    """

    telegram_data = ctx.lifespan_context["telegram_data"]
    await logger.ainfo("tool.get_version", kind="metrics")
    return telegram_data.version


@tool()
async def get_changelog_link(
        ctx: Context,
) -> str:
    """Return the URL of the latest Telegram Bot API changelog.

    Use this when a user asks about recent API changes or migration context.
    """

    telegram_data = ctx.lifespan_context["telegram_data"]
    return telegram_data.changelog_link