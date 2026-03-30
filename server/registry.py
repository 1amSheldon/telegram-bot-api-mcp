from fastmcp import Context

from server.telegram_data import TelegramData


async def get_telegram_data(ctx: Context) -> TelegramData:
    telegram_data = ctx.lifespan_context.get("telegram_data")
    if not isinstance(telegram_data, TelegramData):
        raise RuntimeError("Telegram data registry is not initialized")
    await telegram_data.ensure_fresh()
    return telegram_data
