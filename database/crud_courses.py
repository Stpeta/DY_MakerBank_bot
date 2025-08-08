from datetime import datetime
from typing import TypedDict

from sqlalchemy import select, desc, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Course, Participant, RateHistory


async def create_course(
        session: AsyncSession,
        name: str,
        description: str,
        creator_id: int,
        sheet_url: str | None = None,
        max_loan_amount: float = 100,
        savings_withdrawal_delay: int = 7,
        interest_day: int = 0,
        interest_time: str = "09:00",
) -> Course:
    """Create and commit a new course record."""
    course = Course(
        name=name,
        description=description,
        sheet_url=sheet_url,
        creator_id=creator_id,
        max_loan_amount=max_loan_amount,
        savings_withdrawal_delay=savings_withdrawal_delay,
        interest_day=interest_day,
        interest_time=interest_time,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def get_all_courses_by_admin(
        session: AsyncSession,
        creator_id: int
) -> list[Course]:
    """List all courses by admin, newest first."""
    result = await session.execute(
        select(Course)
        .where(Course.creator_id == creator_id)
        .order_by(desc(Course.created_at))
    )
    return result.scalars().all()


async def get_active_courses_by_admin(
        session: AsyncSession,
        creator_id: int
) -> list[Course]:
    """List active courses for admin."""
    result = await session.execute(
        select(Course)
        .where(Course.creator_id == creator_id, Course.is_active)
        .order_by(desc(Course.created_at))
    )
    return result.scalars().all()


async def finish_course(
        session: AsyncSession,
        course: Course
) -> Course:
    """Mark course as finished and set finish_date."""
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
    """Bulk-insert participants into a course."""
    objs = [Participant(course_id=course_id, **item) for item in data]
    session.add_all(objs)
    await session.commit()


class CourseStats(TypedDict):
    total: int
    registered: int
    avg_balance: float


async def get_course_stats(
        session: AsyncSession,
        course_id: int
) -> CourseStats:
    """Compute stats: total participants, registered count, average balance."""
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


async def set_rate(
        session: AsyncSession,
        course_id: int,
        kind: str,  # "savings" or "loan"
        rate: float
) -> RateHistory:
    """Record new weekly interest rate for savings or loans."""
    entry = RateHistory(
        course_id=course_id,
        kind=kind,
        rate=rate,
        set_at=datetime.utcnow()
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_current_rate(
        session: AsyncSession,
        course_id: int,
        kind: str
) -> float:
    """Retrieve latest weekly interest rate for savings or loans."""
    result = await session.execute(
        select(RateHistory.rate)
        .where(
            RateHistory.course_id == course_id,
            RateHistory.kind == kind
        )
        .order_by(desc(RateHistory.set_at))
        .limit(1)
    )
    return float(result.scalar_one_or_none() or 0.0)
