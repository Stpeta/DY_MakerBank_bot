from database.base import AsyncSessionLocal
from database.crud_participant import get_participant_by_code, register_participant


async def register_by_code(code: str, telegram_id: int, telegram_username: str | None):
    """Register a participant using a code, returning ``(participant, status)``.

    Args:
        code: Registration code provided by the user.
        telegram_id: Telegram identifier of the user.
        telegram_username: Telegram username of the user.

    Returns:
        tuple: A pair ``(participant, status)`` where status is one of:
            - ``"not_found"``: code does not exist.
            - ``"already"``: participant already registered.
            - ``"finished"``: course has been finished.
            - ``"ok"``: registration successful.
    """
    async with AsyncSessionLocal() as session:
        part = await get_participant_by_code(session, code)
        if not part:
            return None, "not_found"
        if part.course and not part.course.is_active:
            return part, "finished"
        if part.is_registered:
            return part, "already"
        part = await register_participant(session, part, telegram_id, telegram_username)
        return part, "ok"
