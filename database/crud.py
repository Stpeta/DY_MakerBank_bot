# crud.py - CRUD functions for MakerBank bot

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict

from sqlalchemy import desc, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models import Course, Participant, Transaction, RateHistory


class CourseStats(TypedDict):
    total: int
    registered: int
    avg_balance: float


# region --- Course CRUD Operations ---
async def create_course(
        session: AsyncSession,
        name: str,
        description: str,
        creator_id: int,
        sheet_url: str | None = None
) -> Course:
    """Create and commit a new course record."""
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
    """Retrieve a course by its unique name."""
    result = await session.execute(
        select(Course).where(Course.name == name)
    )
    return result.scalar_one_or_none()


async def get_latest_course(
        session: AsyncSession
) -> Course | None:
    """Get the most recently created course."""
    result = await session.execute(
        select(Course).order_by(desc(Course.created_at)).limit(1)
    )
    return result.scalar_one_or_none()


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


# endregion --- Course CRUD Operations ---

# region --- Participant Registration & Main Balance ---
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


# endregion --- Participant Registration & Main Balance ---

# region --- Savings/Loan Account Adjustments ---
async def adjust_savings_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float | Decimal
) -> Participant:
    """
    Move coins into (delta>0) or out (delta<0) of savings account, update timestamp.
    Rounds to 2 decimals.
    """
    change = Decimal(delta)
    new_sav = (participant.savings_balance + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    participant.savings_balance = new_sav
    if delta > 0:
        participant.last_savings_deposit_at = datetime.utcnow()
    await session.commit()
    await session.refresh(participant)
    return participant


async def adjust_loan_balance(
        session: AsyncSession,
        participant: Participant,
        delta: float | Decimal
) -> Participant:
    """
    Issue (delta>0) or repay (delta<0) a loan. Rounds to 2 decimals.
    """
    change = Decimal(delta)
    new_loan = (participant.loan_balance + change).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    participant.loan_balance = new_loan
    await session.commit()
    await session.refresh(participant)
    return participant


# endregion --- Savings/Loan Account Adjustments ---

# region --- Course Statistics ---
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


# endregion --- Course Statistics ---

# region --- RateHistory (Interest Rates) ---

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


# endregion --- RateHistory (Interest Rates) ---

# region --- Transaction Management ---
async def create_transaction(
        session: AsyncSession,
        participant_id: int,
        tx_type: str,
        amount: float,
        status: str = "pending"
) -> Transaction:
    """Create a new transaction record with optional pending status."""
    tx = Transaction(
        participant_id=participant_id,
        type=tx_type,
        amount=amount,
        status=status,
        created_at=datetime.utcnow()
    )
    session.add(tx)
    await session.commit()
    await session.refresh(tx)
    return tx


async def get_pending_transactions(
        session: AsyncSession,
        course_id: int
) -> list[Transaction]:
    """Fetch all pending cash deposits and withdrawals for approval."""
    result = await session.execute(
        select(Transaction)
        .join(Participant)
        .where(
            Participant.course_id == course_id,
            Transaction.status == "pending",
            Transaction.type.in_(
                ["cash_withdrawal", "cash_deposit"]
            )
        )
        .order_by(Transaction.created_at)
    )
    return result.scalars().all()


async def update_transaction_status(
        session: AsyncSession,
        tx: Transaction,
        new_status: str
) -> Transaction:
    """Approve or decline a pending transaction and set processed timestamp."""
    tx.status = new_status
    tx.processed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(tx)
    return tx


# endregion --- Transaction Management ---

# region --- Savings Account Adjustments ---
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


# endregion --- Savings Account Adjustments ---

# region --- Loan Account Adjustments ---

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

# endregion --- Loan Account Adjustments ---
