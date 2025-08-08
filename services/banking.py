# services/banking.py

import logging
from datetime import datetime, timedelta
from _decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select

from database.base import AsyncSessionLocal
from database.crud_transactions import create_transaction, update_transaction_status
from database.crud_participant import (
    adjust_participant_balance,
    adjust_savings_balance,
    adjust_loan_balance,
)
from database.crud_courses import get_current_rate
from database.models import Participant, Transaction, Course
from lexicon.lexicon_en import LEXICON

logger = logging.getLogger(__name__)


# region --- Cash Transactions ---

async def create_withdrawal_request(
        participant_id: int,
        amount: int
) -> int:
    # Create a pending withdrawal transaction
    async with AsyncSessionLocal() as session:
        # Fetch participant and check balance
        participant = await session.get(Participant, participant_id)
        if amount <= 0:
            raise ValueError(LEXICON["invalid_amount"])
        if amount > participant.balance:
            raise ValueError(LEXICON["insufficient_funds"])

        # Create pending transaction
        tx = await create_transaction(
            session=session,
            participant_id=participant_id,
            tx_type="cash_withdrawal",
            amount=amount,
            status="pending"
        )

    logger.info(f"Withdrawal request created: tx_id={tx.id}, participant_id={participant_id}, amount={amount}")
    return tx.id


async def create_deposit_request(
        participant_id: int,
        amount: int
) -> int:
    # Create a pending deposit transaction
    async with AsyncSessionLocal() as session:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        tx = await create_transaction(
            session=session,
            participant_id=participant_id,
            tx_type="cash_deposit",
            amount=amount,
            status="pending"
        )

    logger.info(f"Deposit request created: tx_id={tx.id}, participant_id={participant_id}, amount={amount}")
    return tx.id


async def cancel_transaction(
        participant_id: int,
        tx_id: int
) -> None:
    # Cancel a pending transaction belonging to the given participant
    async with AsyncSessionLocal() as session:
        await update_transaction_status(
            session,
            await session.get(Transaction, tx_id),
            "canceled",
        )
    logger.info(f"Transaction canceled by participant: tx_id={tx_id}, participant_id={participant_id}")

# endregion --- Cash Transactions ---


# region --- Savings and Loans ---

async def move_to_savings(participant_id: int, amount: Decimal | float) -> None:
    """Transfer amount from main balance to savings immediately."""
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise ValueError(LEXICON["invalid_amount"])
        if amount > participant.balance:
            raise ValueError(LEXICON["insufficient_funds"])

        await adjust_participant_balance(session, participant, -amount)
        await adjust_savings_balance(session, participant, amount)
        await create_transaction(
            session,
            participant_id=participant_id,
            tx_type="savings_deposit",
            amount=amount,
            status="completed",
        )


async def withdraw_from_savings(participant_id: int, amount: Decimal | float) -> None:
    """Move funds from savings back to main balance respecting lock period."""
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        course = await session.get(Course, participant.course_id)
        amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise ValueError(LEXICON["invalid_amount"])
        if amount > participant.savings_balance:
            raise ValueError(LEXICON["savings_insufficient"])
        last = participant.last_savings_deposit_at
        if last and datetime.utcnow() - last < timedelta(days=course.savings_withdrawal_delay):
            unlock_time = last + timedelta(days=course.savings_withdrawal_delay)
            raise ValueError(LEXICON["savings_locked_until"].format(unlock_time=unlock_time))

        await adjust_savings_balance(session, participant, -amount)
        await adjust_participant_balance(session, participant, amount)
        await create_transaction(
            session,
            participant_id=participant_id,
            tx_type="savings_withdraw",
            amount=amount,
            status="completed",
        )


async def take_loan(participant_id: int, amount: Decimal | float) -> None:
    """Issue a loan to participant up to course limit."""
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        course = await session.get(Course, participant.course_id)
        amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise ValueError(LEXICON["invalid_amount"])
        if participant.loan_balance + amount > course.max_loan_amount:
            raise ValueError(
                LEXICON["loan_limit_reached"].format(limit=course.max_loan_amount)
            )

        await adjust_loan_balance(session, participant, amount)
        await adjust_participant_balance(session, participant, amount)
        await create_transaction(
            session,
            participant_id=participant_id,
            tx_type="loan_borrow",
            amount=amount,
            status="completed",
        )


async def repay_loan(participant_id: int, amount: Decimal | float) -> None:
    """Repay part of the loan from main balance."""
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise ValueError(LEXICON["invalid_amount"])
        if amount > participant.balance:
            raise ValueError(LEXICON["insufficient_funds"])
        if amount > participant.loan_balance:
            raise ValueError(LEXICON["loan_repay_exceeds_loan_balance"])

        await adjust_participant_balance(session, participant, -amount)
        await adjust_loan_balance(session, participant, -amount)
        await create_transaction(
            session,
            participant_id=participant_id,
            tx_type="loan_repay",
            amount=amount,
            status="completed",
        )


async def apply_weekly_interest(course_id: int) -> None:
    """Apply weekly interest for all participants of a course."""
    async with AsyncSessionLocal() as session:
        savings_rate = await get_current_rate(session, course_id, "savings")
        loan_rate = await get_current_rate(session, course_id, "loan")
        result = await session.execute(
            select(Participant).where(Participant.course_id == course_id)
        )
        participants = result.scalars().all()
        for p in participants:
            if savings_rate and p.savings_balance > 0:
                s_rate = Decimal(savings_rate)
                interest = (p.savings_balance * s_rate / Decimal(100)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                await adjust_savings_balance(session, p, interest)
                await create_transaction(
                    session,
                    participant_id=p.id,
                    tx_type="savings_interest",
                    amount=interest,
                    status="completed",
                )
            if loan_rate and p.loan_balance > 0:
                l_rate = Decimal(loan_rate)
                interest = (p.loan_balance * l_rate / Decimal(100)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                await adjust_loan_balance(session, p, interest)
                await create_transaction(
                    session,
                    participant_id=p.id,
                    tx_type="loan_interest",
                    amount=interest,
                    status="completed",
                )

# endregion --- Savings and Loans ---
