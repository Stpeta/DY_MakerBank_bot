# services/course_service.py

from database.crud_courses import create_course, add_participants, set_rate
from services.utils import gen_registration_code
from database.base import AsyncSessionLocal
from database.models import Course, Participant
from sqlalchemy import select
from services.google_sheets import fetch_students, write_registration_codes


async def create_course_with_participants(
        name: str,
        description: str,
        creator_id: int,
        sheet_url: str,
        participants_raw: list[tuple[str, str]],
        savings_rate: float,
        loan_rate: float,
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
        await set_rate(session, course.id, "savings", savings_rate)
        await set_rate(session, course.id, "loan", loan_rate)

    return course, codes_map


async def create_course_basic(
        name: str,
        description: str,
        creator_id: int,
        sheet_url: str,
        savings_rate: float,
        loan_rate: float,
) -> Course:
    """Создаёт курс без участников и задаёт ставки."""
    async with AsyncSessionLocal() as session:
        course = await create_course(
            session,
            name=name,
            description=description,
            creator_id=creator_id,
            sheet_url=sheet_url,
        )
        await set_rate(session, course.id, "savings", savings_rate)
        await set_rate(session, course.id, "loan", loan_rate)
    return course


async def add_new_participants_from_sheet(course_id: int) -> dict[str, str]:
    """Читает таблицу и добавляет новых участников, возвращает карту email->код."""
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        result = await session.execute(
            select(Participant.email, Participant.registration_code).where(
                Participant.course_id == course_id
            )
        )
        existing_rows = result.all()

    existing_emails = {row[0].strip().lower() for row in existing_rows}
    existing_codes = {row[1] for row in existing_rows}

    participants_raw = fetch_students(course.sheet_url)
    new_participants = []
    codes_map: dict[str, str] = {}

    for name_, email in participants_raw:
        email_norm = email.strip().lower()
        if not email_norm or email_norm in existing_emails:
            continue
        code = gen_registration_code(existing_codes)
        existing_codes.add(code)
        existing_emails.add(email_norm)
        new_participants.append({
            "name": name_,
            "email": email,
            "registration_code": code,
        })
        codes_map[email] = code

    if new_participants:
        async with AsyncSessionLocal() as session:
            await add_participants(session, course_id, new_participants)

    if codes_map:
        write_registration_codes(course.sheet_url, codes_map)

    return codes_map
