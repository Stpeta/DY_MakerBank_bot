# database/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func, case
from datetime import datetime
from typing import TypedDict

from database.models import Course, Participant

class CourseStats(TypedDict):
    total: int
    registered: int
    avg_balance: float

async def create_course(
    session: AsyncSession,
    name: str,
    description: str,
    creator_id: int,
    sheet_url: str | None = None
) -> Course:
    course = Course(
        name=name,
        description=description,
        sheet_url=sheet_url,
        creator_id=creator_id
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course

async def get_course_by_name(
    session: AsyncSession,
    name: str
) -> Course | None:
    res = await session.execute(
        select(Course).where(Course.name == name)
    )
    return res.scalar_one_or_none()

async def get_latest_course(
    session: AsyncSession
) -> Course | None:
    res = await session.execute(
        select(Course)
        .order_by(desc(Course.created_at))
        .limit(1)
    )
    return res.scalar_one_or_none()

async def get_all_courses_by_admin(
    session: AsyncSession,
    creator_id: int
) -> list[Course]:
    res = await session.execute(
        select(Course)
        .where(Course.creator_id == creator_id)
        .order_by(desc(Course.created_at))
    )
    return res.scalars().all()

async def get_active_courses_by_admin(
    session: AsyncSession,
    creator_id: int
) -> list[Course]:
    res = await session.execute(
        select(Course)
        .where(Course.creator_id == creator_id, Course.is_active == True)
        .order_by(desc(Course.created_at))
    )
    return res.scalars().all()

async def finish_course(
    session: AsyncSession,
    course: Course
) -> Course:
    course.is_active = False
    course.finish_date = datetime.utcnow()
    await session.commit()
    await session.refresh(course)
    return course

async def add_participants(
    session: AsyncSession,
    course_id: int,
    data: list[dict]
) -> None:
    objs = [Participant(course_id=course_id, **d) for d in data]
    session.add_all(objs)
    await session.commit()

async def get_participant_by_code(
    session: AsyncSession,
    code: str
) -> Participant | None:
    res = await session.execute(
        select(Participant).where(Participant.registration_code == code)
    )
    return res.scalar_one_or_none()

async def register_participant(
    session: AsyncSession,
    participant: Participant,
    telegram_id: int
) -> Participant:
    participant.telegram_id = telegram_id
    participant.is_registered = True
    await session.commit()
    await session.refresh(participant)
    return participant

async def update_participant_balance(
    session: AsyncSession,
    participant: Participant,
    delta: int
) -> Participant:
    participant.balance += delta
    await session.commit()
    await session.refresh(participant)
    return participant

async def get_course_stats(
    session: AsyncSession,
    course_id: int
) -> CourseStats:
    """
    Возвращает: общее число участников,
                 число зарегистрированных и
                 средний баланс.
    """
    stmt = select(
        func.count(Participant.id),
        func.sum(case((Participant.is_registered, 1), else_=0)),
        func.avg(Participant.balance)
    ).where(Participant.course_id == course_id)

    total, registered, avg_balance = (await session.execute(stmt)).one()
    return CourseStats(
        total=total,
        registered=registered,
        avg_balance=float(avg_balance or 0.0)
    )
