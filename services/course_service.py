from database.crud_courses import create_course, add_participants, set_rate
from services.utils import gen_registration_code
from database.base import AsyncSessionLocal
from database.models import Course


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
