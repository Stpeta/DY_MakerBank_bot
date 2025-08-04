from sqlalchemy import select
from config_data.config import load_config
from database.base import AsyncSessionLocal
from database.models import Participant

config = load_config()

async def get_user_role(telegram_id: int) -> str:
    """
    Возвращает одну из ролей: "admin" | "participant" | "guest".
    """
    # Сначала проверяем, админ ли пользователь
    if telegram_id in config.tg_bot.admin_ids:
        return "admin"

    # Иначе — ищем в таблице participants
    async with AsyncSessionLocal() as session:
        part = await session.execute(
            select(Participant).where(Participant.telegram_id == telegram_id)
        )
        part = part.scalar_one_or_none()

    if part and part.is_registered:
        return "participant"
    return "guest"
