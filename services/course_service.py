# services/course_service.py

from database.crud import create_course, add_participants
from services.utils import gen_registration_code
from database.base import AsyncSessionLocal
from database.models import Participant, Course
from sqlalchemy import select


async def create_course_with_participants(
        name: str,
        description: str,
        creator_id: int,
        sheet_url: str,
        participants_raw: list[tuple[str, str]],
) -> tuple[Course, dict[str, str]]:
    """
    1) Берёт сырые данные [(name,email),…] из Google Sheet
    2) Генерирует для каждого регистрационный код
    3) Сохраняет курс и участников в БД
    4) Возвращает (course, codes_map), где codes_map[email]=code
    """
    existing = set()
    participants = []
    codes_map = {}

    # Генерация кодов
    for name_, email in participants_raw:
        code = gen_registration_code(existing)
        existing.add(code)
        participants.append({
            "name": name_,
            "email": email,
            "registration_code": code
        })
        codes_map[email] = code

    # Запись в БД
    async with AsyncSessionLocal() as session:
        course = await create_course(
            session,
            name=name,
            description=description,
            creator_id=creator_id,
            sheet_url=sheet_url
        )
        await add_participants(session, course.id, participants)

    return course, codes_map


async def get_course_creator_id_for_participant(telegram_id: int) -> int | None:
    """
    Given a participant's Telegram ID, return the Telegram ID of the course creator (admin).
    Returns None if participant or course not found.
    """
    async with AsyncSessionLocal() as session:
        # Load participant with its course in one go
        result = await session.execute(
            select(Participant)
            .options(selectinload(Participant.course))
            .where(Participant.telegram_id == telegram_id)
        )
        participant = result.scalar_one_or_none()
        if not participant or not participant.course:
            return None
        return participant.course.creator_id
