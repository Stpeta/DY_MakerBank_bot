import asyncio
import logging

from core.bot import create_bot, create_dispatcher, setup_main_menu
from core.db import init_db
from services.scheduler import interest_scheduler

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the bot."""
    bot = create_bot()
    dp = create_dispatcher()

    await setup_main_menu(bot)
    await init_db()

    asyncio.create_task(interest_scheduler(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("Bot started successfully.")
