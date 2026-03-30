import structlog
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from structlog.typing import FilteringBoundLogger

from server.config import Settings
from server.logs import setup_logging
from server.telegram_data import TelegramData
from server.tools import get_tools

logger: FilteringBoundLogger = structlog.get_logger()


@lifespan
async def lifespan(server):
    settings = Settings()
    telegram_data = TelegramData(
        api_url=settings.app.api_url,
        refresh_ttl_seconds=settings.app.refresh_ttl_seconds,
    )
    await telegram_data.load_api_data()
    try:
        yield {"telegram_data": telegram_data}
    finally:
        pass


def main():
    settings = Settings()
    setup_logging(settings.logs)
    logger.info("Telegram Bot API MCP Server is ready")
    mcp = FastMCP(
        name="Telegram Bot API Docs MCP",
        lifespan=lifespan,
    )
    for tool in get_tools():
        mcp.add_tool(tool)
    if settings.app.proto == "stdio":
        mcp.run(transport="stdio")
        return

    mcp.run(
        transport="http",
        host=settings.app.host,
        port=settings.app.port,
    )



if __name__ == "__main__":
    main()
