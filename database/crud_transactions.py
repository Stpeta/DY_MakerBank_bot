from datetime import datetime, timezone

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
        created_at=datetime.now(timezone.utc)
    )
    session.add(tx)
    await session.commit()
    await session.refresh(tx)
    return tx


async def update_transaction_status(
        session: AsyncSession,
        tx: Transaction,
        new_status: str
) -> Transaction:
    """Approve or decline a pending transaction and set processed timestamp."""
    tx.status = new_status
    tx.processed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(tx)
    return tx
