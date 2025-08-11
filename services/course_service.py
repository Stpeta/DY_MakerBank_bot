import logging
from sqlalchemy import select

from database.crud_courses import (
    create_course as create_course_record,
    add_participants,
    set_rate,
)
from services.utils import gen_registration_code
from services.google_sheets import (
    create_course_sheet,
    fetch_students,
    write_registration_codes,
)
from database.base import AsyncSessionLocal
from database.models import Course, Participant

logger = logging.getLogger(__name__)


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
        course = await create_course_record(
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


async def create_course(
        name: str,
        description: str,
        creator_id: int,
        savings_rate: float,
        loan_rate: float,
) -> Course:
    """Create a course and its spreadsheet."""
    sheet_url = create_course_sheet(name)
    async with AsyncSessionLocal() as session:
        course = await create_course_record(
            session,
            name=name,
            description=description,
            creator_id=creator_id,
            sheet_url=sheet_url,
        )
        await set_rate(session, course.id, "savings", savings_rate)
        await set_rate(session, course.id, "loan", loan_rate)
    return course


async def sync_participants_from_sheet(course_id: int) -> int:
    """Add new participants from the course sheet and assign registration codes."""
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        result = await session.execute(
            select(Participant).where(Participant.course_id == course_id)
        )
        participants = result.scalars().all()
        existing_emails = {p.email.strip().lower() for p in participants}
        existing_codes = {p.registration_code for p in participants}
        sheet_url = course.sheet_url

    try:
        students = fetch_students(sheet_url)
    except Exception as e:  # pragma: no cover - external API errors
        logger.exception("Failed to read students for course %s", course_id)
        raise e

    new_participants = []
    codes_map: dict[str, str] = {}

    for name_, email in students:
        email_lc = email.strip().lower()
        if email_lc in existing_emails:
            continue
        code = gen_registration_code(existing_codes)
        existing_codes.add(code)
        new_participants.append({
            "name": name_,
            "email": email,
            "registration_code": code,
        })
        codes_map[email] = code

    if not new_participants:
        return 0

    async with AsyncSessionLocal() as session:
        await add_participants(session, course_id, new_participants)

    write_registration_codes(sheet_url, codes_map)
    return len(new_participants)
