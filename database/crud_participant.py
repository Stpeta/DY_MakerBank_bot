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
    """Return participants registered to the given Telegram account."""
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


async def adjust_wallet_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float | Decimal
) -> Participant:
    """Adjust wallet balance by the given delta rounded to 2 decimals."""
    change = Decimal(delta)
    new_balance = (participant.wallet_balance + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    participant.wallet_balance = new_balance
    await session.commit()
    await session.refresh(participant)
    return participant


async def adjust_savings_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float | Decimal
) -> Participant:
    """Move coins into (delta>0) or out (delta<0) of savings account, update timestamp."""
    change = Decimal(delta)
    new_balance = (participant.savings_balance + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    participant.savings_balance = new_balance
    if change > 0:
        participant.last_savings_deposit_at = datetime.utcnow()
    await session.commit()
    await session.refresh(participant)
    return participant


async def adjust_loan_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float | Decimal
) -> Participant:
    """Issue (delta>0) or repay (delta<0) a loan."""
    change = Decimal(delta)
    new_balance = (participant.loan_balance + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    participant.loan_balance = new_balance
    await session.commit()
    await session.refresh(participant)
    return participant
