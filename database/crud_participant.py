from _decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Participant


async def get_participants_by_telegram_id(
    session: AsyncSession,
    telegram_id: int,
    course_is_active: Optional[bool] = None,
):
    query = (
        select(Participant)
        .options(selectinload(Participant.course))
        .where(
            Participant.telegram_id == telegram_id,
            Participant.is_registered == True,
        )
    )

    if course_is_active is not None:
        query = query.where(Participant.course.has(is_active=course_is_active))

    result = await session.execute(query)
    return result.scalars().all()


async def get_participant_by_code(
        session: AsyncSession,
        code: str
) -> Participant | None:
    """Fetch a participant by their registration code."""
    result = await session.execute(
        select(Participant).where(Participant.registration_code == code)
    )
    return result.scalar_one_or_none()


async def register_participant(
        session: AsyncSession,
        participant: Participant,
        telegram_id: int
) -> Participant:
    """Set Telegram ID and mark participant as registered."""
    participant.telegram_id = telegram_id
    participant.is_registered = True
    await session.commit()
    await session.refresh(participant)
    return participant


async def get_participant_by_id(
        session: AsyncSession,
        participant_id: int,
) -> Participant | None:
    """Fetch a participant by database ID, loading related course."""
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.course))
        .where(Participant.id == participant_id)
    )
    return result.scalar_one_or_none()


async def get_participants_by_course(
        session: AsyncSession,
        course_id: int,
) -> list[Participant]:
    """Return all participants of a given course."""
    result = await session.execute(
        select(Participant).where(Participant.course_id == course_id)
    )
    return result.scalars().all()


async def get_registered_participants_with_telegram(
        session: AsyncSession,
        course_id: int,
) -> list[Participant]:
    """Participants of a course who are registered and have a Telegram ID."""
    result = await session.execute(
        select(Participant).where(
            Participant.course_id == course_id,
            Participant.is_registered,
            Participant.telegram_id.is_not(None),
        )
    )
    return result.scalars().all()


async def adjust_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float | Decimal,
        wallet: str,
) -> Participant:
    """Adjust one of participant's balances (main, savings, loan)."""
    change = Decimal(delta)
    field_map = {
        "balance": "balance",
        "savings": "savings_balance",
        "loan": "loan_balance",
    }
    attr = field_map.get(wallet)
    if not attr:
        raise ValueError("Invalid wallet type")
    new_balance = (getattr(participant, attr) + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    setattr(participant, attr, new_balance)
    if wallet == "savings" and change > 0:
        participant.last_savings_deposit_at = datetime.utcnow()
    await session.commit()
    await session.refresh(participant)
    return participant
