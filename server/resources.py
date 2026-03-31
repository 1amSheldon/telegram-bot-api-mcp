import json
from difflib import get_close_matches
from urllib.parse import unquote

from fastmcp import Context, FastMCP
from pydantic import BaseModel

from server.errors import MethodNotFoundError, TypeNotFoundError
from server.registry import get_telegram_data
from server.schemas import ChangelogResult, ChangelogUpdate, FindResult, MethodList, TypeList, VersionInfo
from server.utils import build_metadata, build_response, format_method, format_type

RESOURCE_SCHEME = "telegram-bot-api"


def _render_json(payload: BaseModel | dict) -> str:
    if isinstance(payload, BaseModel):
        payload = payload.model_dump(mode="json")
    return json.dumps(payload, ensure_ascii=False, indent=2)


def register_resources(mcp: FastMCP) -> None:
    @mcp.resource(
        f"{RESOURCE_SCHEME}://index",
        name="telegram_bot_api_index",
        title="Telegram Bot API index",
        description="Entry point for Telegram Bot API MCP resources and templates.",
        mime_type="application/json",
    )
    async def index_resource(ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        payload = {
            "server": "Telegram Bot API Docs MCP",
            "api_version": telegram_data.current_version,
            "static_resources": [
                f"{RESOURCE_SCHEME}://index",
                f"{RESOURCE_SCHEME}://version",
                f"{RESOURCE_SCHEME}://changelog",
                f"{RESOURCE_SCHEME}://methods",
                f"{RESOURCE_SCHEME}://types",
            ],
            "resource_templates": [
                f"{RESOURCE_SCHEME}://method/{{name}}",
                f"{RESOURCE_SCHEME}://type/{{name}}",
                f"{RESOURCE_SCHEME}://search/{{query}}",
            ],
            "usage_notes": [
                "Read methods/types lists for discovery, then open a method or type template URI for canonical details.",
                "The search template accepts URL-encoded queries, for example telegram-bot-api://search/inline%20keyboard.",
            ],
        }
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://version",
        name="telegram_bot_api_version",
        title="Telegram Bot API version",
        description="Current Telegram Bot API version string.",
        mime_type="application/json",
    )
    async def version_resource(ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        payload = build_response(
            VersionInfo(version=telegram_data.current_version),
            build_metadata(version=telegram_data.current_version),
        )
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://changelog",
        name="telegram_bot_api_changelog",
        title="Telegram Bot API changelog",
        description="Latest cached Telegram Bot API changelog entries.",
        mime_type="application/json",
    )
    async def changelog_resource(ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        payload = build_response(
            ChangelogResult(
                updates=[ChangelogUpdate(**entry) for entry in telegram_data.recent_changelog]
            ),
            build_metadata(version=telegram_data.current_version),
        )
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://methods",
        name="telegram_bot_api_methods",
        title="Telegram Bot API methods",
        description="List of all Telegram Bot API method names.",
        mime_type="application/json",
    )
    async def methods_resource(ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        methods = telegram_data.list_method_names()
        payload = build_response(
            MethodList(
                items=methods,
                total=len(methods),
                limit=len(methods),
                offset=0,
                filter=None,
            ),
            build_metadata(version=telegram_data.current_version),
        )
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://types",
        name="telegram_bot_api_types",
        title="Telegram Bot API types",
        description="List of all Telegram Bot API type names.",
        mime_type="application/json",
    )
    async def types_resource(ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        type_names = list(telegram_data.api_data.get("types", {}).keys())
        payload = build_response(
            TypeList(items=type_names, total=len(type_names)),
            build_metadata(version=telegram_data.current_version),
        )
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://method/{{name}}",
        name="telegram_bot_api_method",
        title="Telegram Bot API method details",
        description="Canonical Telegram Bot API method details by method name.",
        mime_type="application/json",
    )
    async def method_resource(name: str, ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        method_name = unquote(name)
        actual_name = telegram_data.resolve_method_name(method_name)
        if not actual_name:
            available = list(telegram_data.api_data.get("methods", {}).keys())
            suggestions = get_close_matches(method_name, available, n=5, cutoff=0.5)
            raise MethodNotFoundError(name=method_name, suggestions=suggestions)

        method_info = telegram_data.api_data["methods"][actual_name]
        payload = build_response(
            format_method(method_info),
            build_metadata(
                version=telegram_data.current_version,
                documentation_url=method_info.get("href"),
            ),
        )
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://type/{{name}}",
        name="telegram_bot_api_type",
        title="Telegram Bot API type details",
        description="Canonical Telegram Bot API type details by type name.",
        mime_type="application/json",
    )
    async def type_resource(name: str, ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        type_name = unquote(name)
        actual_name = telegram_data.resolve_type_name(type_name)
        if not actual_name:
            raise TypeNotFoundError(type_name)

        type_data = telegram_data.api_data["types"][actual_name]
        payload = build_response(
            format_type(type_data),
            build_metadata(
                version=telegram_data.current_version,
                documentation_url=type_data.get("href"),
            ),
        )
        return _render_json(payload)

    @mcp.resource(
        f"{RESOURCE_SCHEME}://search/{{query}}",
        name="telegram_bot_api_search",
        title="Telegram Bot API search",
        description="Search Telegram Bot API methods and types by URL-encoded query.",
        mime_type="application/json",
    )
    async def search_resource(query: str, ctx: Context) -> str:
        telegram_data = await get_telegram_data(ctx)
        query_text = unquote(query).lower()
        results = {"methods": [], "types": []}
        seen_methods = set()
        seen_types = set()

        for word in query_text.split():
            if word in telegram_data.search_index:
                for item in telegram_data.search_index[word]:
                    if item["type"] == "method" and item["name"] not in seen_methods:
                        seen_methods.add(item["name"])
                        results["methods"].append(item["name"])
                    elif item["type"] == "type" and item["name"] not in seen_types:
                        seen_types.add(item["name"])
                        results["types"].append(item["name"])

        for method_name in telegram_data.api_data.get("methods", {}).keys():
            if query_text in method_name.lower() and method_name not in seen_methods:
                results["methods"].append(method_name)

        for type_name in telegram_data.api_data.get("types", {}).keys():
            if query_text in type_name.lower() and type_name not in seen_types:
                results["types"].append(type_name)

        payload = build_response(
            FindResult(
                methods=results["methods"],
                types=results["types"],
            ),
            build_metadata(version=telegram_data.current_version),
        )
        return _render_json(payload)
