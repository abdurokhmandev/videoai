import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Settings, settings
from bot.database.queries import init_db
from bot.handlers.start import router as start_router
# from bot.handlers.video import router as video_router
# from bot.handlers.payment import router as payment_router
# from bot.handlers.balance import router as balance_router
# from bot.handlers.referral import router as referral_router
# from bot.handlers.settings import router as settings_router
# from bot.handlers.admin import router as admin_router


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)


from bot.middleware.maintenance import MaintenanceMiddleware


def create_dispatcher(settings: Settings) -> Dispatcher:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register maintenance middleware as outer middleware
    dp.message.outer_middleware(MaintenanceMiddleware())
    
    dp.include_router(start_router)
    # dp.include_router(video_router)
    # dp.include_router(payment_router)
    # dp.include_router(balance_router)
    # dp.include_router(referral_router)
    # dp.include_router(settings_router)
    # dp.include_router(admin_router)
    return dp


async def on_startup(bot: Bot) -> None:
    await init_db()


from aiogram.client.default import DefaultBotProperties

async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = create_dispatcher(settings)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_logging()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user")
