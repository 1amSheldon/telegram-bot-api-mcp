import os

os.environ.setdefault("FASTMCP_LOG_ENABLED", "false")
os.environ.setdefault("FASTMCP_SHOW_SERVER_BANNER", "false")

import structlog
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from structlog.typing import FilteringBoundLogger

from server.config import Settings
from server.logs import setup_logging
from server.resources import register_resources
from server.telegram_data import TelegramData
from server.tools import get_tools

logger: FilteringBoundLogger = structlog.get_logger()


@lifespan
async def lifespan(server):
    settings = Settings()
    log_enabled = settings.app.proto != "stdio"
    telegram_data = TelegramData(
        api_url=settings.app.api_url,
        refresh_ttl_seconds=settings.app.refresh_ttl_seconds,
        log_enabled=log_enabled,
    )
    try:
        yield {"telegram_data": telegram_data}
    finally:
        pass


def main():
    settings = Settings()
    if settings.app.proto != "stdio":
        setup_logging(settings.logs)
        logger.info("Telegram Bot API MCP Server is ready")
    mcp = FastMCP(
        name="Telegram Bot API Docs MCP",
        lifespan=lifespan,
    )
    register_resources(mcp)
    for tool in get_tools():
        mcp.add_tool(tool)
    if settings.app.proto == "stdio":
        mcp.run(transport="stdio", show_banner=False)
        return

    mcp.run(
        transport="http",
        host=settings.app.host,
        port=settings.app.port,
    )



if __name__ == "__main__":
    main()
