import structlog
from fastmcp import Context
from fastmcp.tools import tool
from structlog.typing import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()


@tool()
async def find(
        query: str,
        ctx: Context,
) -> dict:
    """Search for methods and types by query string."""

    telegram_data = ctx.lifespan_context["telegram_data"]
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

    await logger.ainfo("tool.find", kind="metrics")
    return results
