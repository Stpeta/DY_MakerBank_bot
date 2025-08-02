import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import load_config
from handlers.admin import admin_router
from handlers.participant import participant_router
from handlers.other import other_router
from database.base import engine, Base

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main() -> None:
    # Load configuration
    config = load_config()
    # Initialization of the bot and dispatcher
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Registration of routers
    dp.include_router(admin_router)
    dp.include_router(participant_router)
    dp.include_router(other_router)

    # Creating tables in the database if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created or already exist.")

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    logger.info("Bot started successfully.")