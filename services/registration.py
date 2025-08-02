from sqlalchemy.future import select
from database.base import AsyncSessionLocal
from database.models import Participant
from config_data.config import load_config

config = load_config()

async def get_user_role(telegram_id: int) -> str:
    if telegram_id in config.tg_bot.admin_ids:
        return "admin"
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Participant).where(Participant.telegram_id == telegram_id)
        )
        part = res.scalar_one_or_none()
    if part and part.is_registered:
        return "participant"
    return "other"