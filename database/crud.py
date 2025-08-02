from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Course, Participant

async def create_course(
    session: AsyncSession,
    name: str,
    description: str,
    creator_id: int,
    sheet_url: str | None = None          # ← добавили параметр
) -> Course:
    course = Course(
        name=name,
        description=description,
        sheet_url=sheet_url,               # ← записываем сюда
        creator_id=creator_id
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course
async def get_course_by_name(session: AsyncSession, name: str):
    res = await session.execute(select(Course).where(Course.name == name))
    return res.scalar_one_or_none()

async def add_participants(session: AsyncSession, course_id: int, data: list[dict]):
    objs = [Participant(course_id=course_id, **d) for d in data]
    session.add_all(objs)
    await session.commit()

async def get_participant_by_code(session: AsyncSession, code: str):
    res = await session.execute(select(Participant).where(Participant.registration_code == code))
    return res.scalar_one_or_none()

async def register_participant(session: AsyncSession, participant: Participant, telegram_id: int):
    participant.telegram_id = telegram_id
    participant.is_registered = True
    await session.commit()
    await session.refresh(participant)
    return participant

async def update_participant_balance(session: AsyncSession, participant: Participant, delta: int):
    participant.balance += delta
    await session.commit()
    await session.refresh(participant)
    return participant