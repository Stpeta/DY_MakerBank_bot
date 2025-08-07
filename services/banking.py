# services/banking.py

import logging

from database.base import AsyncSessionLocal
from database.crud_transactions import create_transaction, update_transaction_status
from database.models import Participant, Transaction
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
