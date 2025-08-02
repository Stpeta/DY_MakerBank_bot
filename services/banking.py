from database.base import AsyncSessionLocal
from database.crud import get_participant_by_code, update_participant_balance

async def deposit(telegram_id: int, amount: int):
    async with AsyncSessionLocal() as session:
        part = await get_participant_by_code(session, telegram_id=telegram_id)
        if not part or not part.is_registered:
            return None
        return await update_participant_balance(session, part, amount)