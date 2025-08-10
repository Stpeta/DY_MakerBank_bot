from config_data import config
from database.base import AsyncSessionLocal
from database.crud_participant import get_participants_by_telegram_id


async def get_user_role(telegram_id: int) -> str:
    """
    Возвращает одну из ролей: "admin" | "participant" | "guest".
    """
    # Сначала проверяем, админ ли пользователь
    if telegram_id in config.tg_bot.admin_ids:
        return "admin"

    # Иначе — ищем участника с активным курсом
    async with AsyncSessionLocal() as session:
        participants = await get_participants_by_telegram_id(
            session,
            telegram_id,
            course_is_active=True,
        )

    if participants:
        return "participant"
    return "guest"
