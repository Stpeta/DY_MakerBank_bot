import asyncio
from datetime import datetime, timedelta, time
from sqlalchemy import select

from database.base import AsyncSessionLocal
from database.models import Course, Participant, Transaction
from services.banking import apply_weekly_interest


async def interest_scheduler(poll_interval: int = 60) -> None:
    """Periodically apply weekly interest for courses on scheduled day/time."""
    while True:
        now = datetime.utcnow()
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Course).where(Course.is_active))
            courses = result.scalars().all()
            for course in courses:
                try:
                    hour, minute = map(int, course.interest_time.split(":"))
                except ValueError:
                    # skip invalid time format
                    continue
                week_start = now.date() - timedelta(days=now.weekday())
                interest_date = week_start + timedelta(days=course.interest_day)
                scheduled_dt = datetime.combine(interest_date, time(hour, minute))
                if now >= scheduled_dt:
                    stmt = (
                        select(Transaction.id)
                        .join(Participant)
                        .where(
                            Participant.course_id == course.id,
                            Transaction.type.in_(["savings_interest", "loan_interest"]),
                            Transaction.created_at >= scheduled_dt,
                        )
                        .limit(1)
                    )
                    existing = await session.execute(stmt)
                    if existing.scalar_one_or_none() is None:
                        await apply_weekly_interest(course.id)
        await asyncio.sleep(poll_interval)
