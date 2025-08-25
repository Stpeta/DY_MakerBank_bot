import logging
from aiogram import Bot, Dispatcher
from config_data import config
from handlers import register_handlers
from keyboards.main_menu import get_main_menu_commands
from middlewares.logging_middleware import LoggingMiddleware

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Create and return a Bot instance using configuration."""
    return Bot(token=config.tg_bot.token)


def create_dispatcher() -> Dispatcher:
    """Create dispatcher and register all handlers."""
    dp = Dispatcher()
    dp.update.outer_middleware(LoggingMiddleware())
    register_handlers(dp)
    return dp


async def setup_main_menu(bot: Bot) -> None:
    """Install global bot commands menu."""
    commands = get_main_menu_commands()
    await bot.set_my_commands(commands)
    logger.info("Main menu commands set: %s", commands)
