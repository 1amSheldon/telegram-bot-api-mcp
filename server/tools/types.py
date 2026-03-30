from fastmcp import Context
from fastmcp.tools import tool

from server.errors import TypeNotFoundError
from server.registry import get_telegram_data
from server.schemas import Response, TypeDetail, TypeList
from server.metrics import metrics
from server.utils import build_metadata, build_response, format_type


@tool()
@metrics("tool.resolve_type")
async def resolve_type(
        name: str,
        ctx: Context,
) -> Response[TypeDetail]:
    """Return canonical details for a Telegram Bot API type by name.

    Use this to verify field names, field types, and constraints for a Bot API
    object before generating or reviewing code.
    """

    telegram_data = await get_telegram_data(ctx)
    actual_name = telegram_data.resolve_type_name(name)

    if not actual_name:
        raise TypeNotFoundError(name)

    type_data = telegram_data.api_data["types"][actual_name]
    detail = format_type(type_data)
    metadata = build_metadata(
        version=telegram_data.current_version,
        documentation_url=type_data.get("href"),
    )
    return build_response(detail, metadata)


@tool()
@metrics("tool.list_types")
async def list_types(
        ctx: Context,
) -> Response[TypeList]:
    """List all Telegram Bot API type names.

    Use this for discovery when the exact type name is unknown, then call
    ``resolve_type`` for detailed type information.
    """

    telegram_data = await get_telegram_data(ctx)
    items = list(telegram_data.api_data.get("types", {}).keys())
    payload = TypeList(items=items, total=len(items))
    metadata = build_metadata(
        version=telegram_data.current_version,
    )
    return build_response(payload, metadata)
