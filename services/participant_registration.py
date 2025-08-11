from database.base import AsyncSessionLocal
from database.crud_participant import get_participant_by_code, register_participant


async def register_by_code(code: str, telegram_id: int):
    """Register a participant using a code, returning (participant, status)."""
    async with AsyncSessionLocal() as session:
        part = await get_participant_by_code(session, code)
        if not part:
            return None, "not_found"
        if part.is_registered:
            return part, "already"
        part = await register_participant(session, part, telegram_id)
        return part, "ok"
