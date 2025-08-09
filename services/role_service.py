from sqlalchemy import select
from config_data import config
from database.base import AsyncSessionLocal
from database.models import Participant

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
        part = part.scalars().first()
        
    if part and part.is_registered:
        return "participant"
    return "guest"

