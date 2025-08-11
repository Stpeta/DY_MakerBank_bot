import asyncio
from datetime import datetime, timedelta, time

from aiogram import Bot

from database.base import AsyncSessionLocal
from database.crud_courses import get_active_courses
from services.banking import apply_weekly_interest


async def interest_scheduler(bot: Bot, poll_interval: int = 300) -> None:
    """Periodically apply weekly interest for courses on scheduled day/time."""
    while True:
        now = datetime.utcnow()
        async with AsyncSessionLocal() as session:
            courses = await get_active_courses(session)
            for course in courses:
                try:
                    hour, minute = map(int, course.interest_time.split(":"))
                except ValueError:
                    # skip invalid time format
                    continue
                week_start = now.date() - timedelta(days=now.weekday())
                interest_date = week_start + timedelta(days=course.interest_day)
                scheduled_dt = datetime.combine(interest_date, time(hour, minute))
                if now >= scheduled_dt > course.last_interest_at:
                    await apply_weekly_interest(course.id, bot)
        await asyncio.sleep(poll_interval)
