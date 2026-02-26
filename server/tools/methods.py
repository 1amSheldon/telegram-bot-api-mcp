from difflib import get_close_matches
from fastmcp import Context
from fastmcp.tools import tool

from server.errors import MethodNotFoundError
from server.registry import get_telegram_data
from server.schemas import MethodDetail, MethodList, Response
from server.metrics import metrics
from server.utils import build_metadata, build_response, format_method

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@tool()
@metrics("tool.resolve_method")
async def resolve_method(
        name: str,
        ctx: Context,
) -> Response[MethodDetail]:
    """Return canonical details for a Telegram Bot API method by name.

    Use this to verify method parameters, return type, and field semantics against
    the official Bot API spec before giving implementation advice.

    If lookup fails, try ``list_methods`` with ``filter`` to discover a close match.
    """

    telegram_data = get_telegram_data(ctx)
    actual_name = telegram_data.resolve_method_name(name)
    if not actual_name:
        available = list(telegram_data.api_data.get("methods", {}).keys())
        suggestions = get_close_matches(name, available, n=5, cutoff=0.5)
        raise MethodNotFoundError(name=name, suggestions=suggestions)

    method_info = telegram_data.api_data["methods"][actual_name]
    detail: MethodDetail = format_method(method_info)
    metadata = build_metadata(
        version=telegram_data.current_version,
        documentation_url=method_info.get("href"),
    )
    return build_response(detail, metadata)


@tool()
@metrics("tool.list_methods")
async def list_methods(
        ctx: Context,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        filter: str | None = None,
) -> Response[MethodList]:
    """List all Telegram Bot API method names.

    Use this for discovery when the exact method is unknown, then call
    ``resolve_method`` for full method details.

    Use ``limit``/``offset`` to control context usage and ``filter`` to narrow
    discovery to a topic keyword, such as ``stickers`` or ``passport``.
    """

    if limit <= 0:
        raise ValueError("Parameter 'limit' must be a positive integer")
    if limit > MAX_LIMIT:
        raise ValueError(f"Parameter 'limit' must be <= {MAX_LIMIT}")
    if offset < 0:
        raise ValueError("Parameter 'offset' must be >= 0")

    telegram_data = get_telegram_data(ctx)
    methods = telegram_data.list_method_names(filter)
    total = len(methods)
    items = methods[offset: offset + limit]

    payload = MethodList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filter=filter,
    )
    metadata = build_metadata(
        version=telegram_data.current_version,
    )
    return build_response(payload, metadata)