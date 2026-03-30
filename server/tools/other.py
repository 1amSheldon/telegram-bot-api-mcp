from fastmcp import Context
from fastmcp.tools import tool
 
from server.registry import get_telegram_data
from server.schemas import ChangelogResult, ChangelogUpdate, Response, VersionInfo
from server.metrics import metrics
from server.utils import build_metadata, build_response


@tool()
@metrics("tool.get_version")
async def get_version(
        ctx: Context,
) -> Response[VersionInfo]:
    """Return the current Telegram Bot API version.

    Use this when version-specific behavior may affect implementation guidance.
    """

    telegram_data = await get_telegram_data(ctx)
    payload = VersionInfo(version=telegram_data.current_version)
    metadata = build_metadata(
        version=telegram_data.current_version,
    )
    return build_response(payload, metadata)


@tool()
@metrics("tool.changelog")
async def changelog(
        ctx: Context,
) -> Response[ChangelogResult]:
    """Return latest Telegram Bot API changelog updates from startup cache.

    Use this when a user asks about recent API changes. Returns the latest
    parsed release entries with plain-text bullet points.
    """

    telegram_data = await get_telegram_data(ctx)
    payload = ChangelogResult(
        updates=[ChangelogUpdate(**entry) for entry in telegram_data.recent_changelog]
    )
    metadata = build_metadata(
        version=telegram_data.current_version,
    )
    return build_response(payload, metadata)
