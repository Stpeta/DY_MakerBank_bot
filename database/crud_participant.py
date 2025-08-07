from _decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Participant


async def get_participant_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
) -> Participant | None:
    """Fetch a registered participant by their Telegram ID."""
    result = await session.execute(
        select(Participant).where(
            Participant.telegram_id == telegram_id,
            Participant.is_registered == True
        )
    )
    return result.scalar_one_or_none()


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


async def adjust_participant_balance(
    session: AsyncSession,
    participant: Participant,
    delta: float | Decimal
) -> Participant:
    """
    Adjust main wallet balance by the given delta (can be fractional).
    Rounds to 2 decimals.
    """
    # Ensure Decimal
    change = Decimal(delta)
    new_balance = (participant.balance + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    participant.balance = new_balance
    await session.commit()
    await session.refresh(participant)
    return participant


async def adjust_savings_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float
) -> Participant:
    """Move coins into (delta>0) or out (delta<0) of savings account, update timestamp."""
    participant.savings_balance += delta
    if delta > 0:
        participant.last_savings_deposit_at = datetime.utcnow()
    await session.commit()
    await session.refresh(participant)
    return participant


async def adjust_loan_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float
) -> Participant:
    """Issue (delta>0) or repay (delta<0) a loan."""
    participant.loan_balance += delta
    await session.commit()
    await session.refresh(participant)
    return participant
