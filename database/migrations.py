import asyncio
from datetime import datetime
from sqlalchemy import text

from database.base import engine


async def add_last_interest_at_column() -> None:
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(courses)"))
        columns = [row[1] for row in result.fetchall()]
        if "last_interest_at" not in columns:
            await conn.execute(text("ALTER TABLE courses ADD COLUMN last_interest_at DATETIME"))
            await conn.execute(
                text("UPDATE courses SET last_interest_at = :now"),
                {"now": datetime.utcnow()},
            )


if __name__ == "__main__":
    asyncio.run(add_last_interest_at_column())

