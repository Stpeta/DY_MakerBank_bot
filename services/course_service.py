from sqlalchemy import select

from database.crud_courses import create_course, add_participants, set_rate
from services.utils import gen_registration_code
from database.base import AsyncSessionLocal
from database.models import Course, Participant
from services.google_sheets import fetch_students, write_registration_codes, mark_registered
from lexicon.lexicon_en import LEXICON


async def create_course_with_participants(
        name: str,
        description: str,
        creator_id: int,
        sheet_url: str,
        participants_raw: list[tuple[str, str]],
        savings_rate: float,
        loan_rate: float,
) -> tuple[Course, dict[str, str]]:
    """Create a course with participants and return it plus registration codes."""
    existing = set()
    participants = []
    codes_map = {}

    # Generate unique registration codes
    for name_, email in participants_raw:
        code = gen_registration_code(existing)
        existing.add(code)
        participants.append({
            "name": name_,
            "email": email,
            "registration_code": code,
        })
        codes_map[email] = code

    # Persist course and participants
    async with AsyncSessionLocal() as session:
        course = await create_course(
            session,
            name=name,
            description=description,
            creator_id=creator_id,
            sheet_url=sheet_url,
        )
        await add_participants(session, course.id, participants)
        await set_rate(session, course.id, "savings", savings_rate)
        await set_rate(session, course.id, "loan", loan_rate)

    return course, codes_map


async def sync_course_participants(course_id: int) -> int:
    """Synchronize Google Sheet participants with the database."""
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        rows = fetch_students(course.sheet_url)

        result = await session.execute(
            select(Participant.email, Participant.registration_code, Participant.is_registered)
            .where(Participant.course_id == course_id)
        )
        existing = {
            email.lower(): (code, is_registered)
            for email, code, is_registered in result
        }
        existing_codes = {data[0] for data in existing.values()}

        new_participants: list[dict[str, str]] = []
        codes_map: dict[str, str] = {}

        for row in rows:
            name = row.get(LEXICON["sheet_header_name"], "").strip()
            email = row.get(LEXICON["sheet_header_email"], "").strip()
            if not name or not email or email.lower() in existing:
                continue
            code = gen_registration_code(existing_codes)
            existing_codes.add(code)
            new_participants.append({
                "name": name,
                "email": email,
                "registration_code": code,
            })
            codes_map[email] = code

        if new_participants:
            await add_participants(session, course_id, new_participants)

        registered_emails = {
            email for email, data in existing.items() if data[1]
        }

    write_registration_codes(course.sheet_url, codes_map)
    for email in registered_emails:
        mark_registered(course.sheet_url, email)
    return len(codes_map)
