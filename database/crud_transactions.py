from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Transaction, Participant


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
