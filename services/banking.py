import logging

from database.base import AsyncSessionLocal
from database.crud import (
    get_participant_by_telegram_id,
    create_transaction,
    update_transaction_status
)
from database.models import Transaction

logger = logging.getLogger(__name__)


# region --- Cash Transactions ---

async def create_withdrawal_request(
        telegram_id: int,
        amount: int
) -> int:
    """
    Create a pending withdrawal transaction.
    Raises ValueError if the amount is not positive or exceeds available balance.
    Returns the new tx.id.
    """
    async with AsyncSessionLocal() as session:
        # Fetch participant and check balance
        participant = await get_participant_by_telegram_id(session, telegram_id)
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > participant.balance:
            raise ValueError("Insufficient funds for withdrawal.")

        # Create pending transaction
        tx = await create_transaction(
            session=session,
            participant_id=participant.id,
            tx_type="cash_withdrawal",
            amount=amount,
            status="pending"
        )

    logger.info(f"Withdrawal request created: tx_id={tx.id}, user_id={telegram_id}, amount={amount}")
    return tx.id


async def create_deposit_request(
        telegram_id: int,
        amount: int
) -> int:
    """
    Create a pending deposit transaction.
    Returns the new tx.id.
    Raises ValueError on invalid amount.
    """
    async with AsyncSessionLocal() as session:
        participant = await get_participant_by_telegram_id(session, telegram_id)
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        tx = await create_transaction(
            session=session,
            participant_id=participant.id,
            tx_type="cash_deposit",
            amount=amount,
            status="pending"
        )

    logger.info(f"Deposit request created: tx_id={tx.id}, user_id={telegram_id}, amount={amount}")
    return tx.id


async def cancel_transaction(
        telegram_id: int,
        tx_id: int
) -> None:
    """
    Cancel a pending transaction belonging to the given participant.
    """
    async with AsyncSessionLocal() as session:
        # we assume update_transaction_status will load and update tx
        await update_transaction_status(session,
                                        await session.get(Transaction, tx_id),
                                        "canceled"
                                        )
    logger.info(f"Transaction canceled by user: tx_id={tx_id}, user_id={telegram_id}")

# endregion --- Cash Transactions ---
