from fastmcp import Context
from fastmcp.tools import tool
 
from server.registry import get_telegram_data
from server.schemas import FindResult, Response
from server.metrics import metrics
from server.utils import build_metadata, build_response


@tool()
@metrics("tool.find")
async def find(
        query: str,
        ctx: Context,
) -> Response[FindResult]:
    """Search Telegram Bot API methods and types by natural-language query.

    Use this as a first step when the exact API entity is unclear (for example,
    "edit message" or "reply keyboard"), then call ``resolve_method`` or
    ``resolve_type`` on the returned names for canonical details.
    DO NOT use for finding latest API updates or version history.
    """

    telegram_data = await get_telegram_data(ctx)
    query_lower = query.lower()
    results = {"methods": [], "types": []}

    seen_methods = set()
    seen_types = set()

    for word in query_lower.split():
        if word in telegram_data.search_index:
            for item in telegram_data.search_index[word]:
                if item["type"] == "method" and item["name"] not in seen_methods:
                    seen_methods.add(item["name"])
                    results["methods"].append(item["name"])
                elif item["type"] == "type" and item["name"] not in seen_types:
                    seen_types.add(item["name"])
                    results["types"].append(item["name"])

    for method_name in telegram_data.api_data.get("methods", {}).keys():
        if query_lower in method_name.lower() and method_name not in seen_methods:
            results["methods"].append(method_name)

    for type_name in telegram_data.api_data.get("types", {}).keys():
        if query_lower in type_name.lower() and type_name not in seen_types:
            results["types"].append(type_name)

    payload = FindResult(
        methods=results["methods"],
        types=results["types"],
    )
    metadata = build_metadata(
        version=telegram_data.current_version,
    )
    return build_response(payload, metadata)
