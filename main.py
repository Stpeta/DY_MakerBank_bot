import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import load_config
from database.base import engine, Base
from handlers.common import common_router
from handlers.admin import admin_router
from handlers.participant import participant_router
from handlers.guest import guest_router
from keyboards.main_menu import get_main_menu_commands

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main() -> None:
    # 1) Загрузка конфига и инициализация бота
    config = load_config()
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # 2) Роутеры
    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(participant_router)
    dp.include_router(guest_router)

    # 3) Установка общего меню команд
    commands = get_main_menu_commands()
    await bot.set_my_commands(commands)
    logger.info("Main menu commands set: %s", commands)

    # 4) Создание таблиц в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created or already exist.")

    # 5) Старт polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    logger.info("Bot started successfully.")
