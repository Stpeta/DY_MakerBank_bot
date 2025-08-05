from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.base import AsyncSessionLocal
from database.models import Participant
from lexicon.lexicon_en import LEXICON
from keyboards.participant import main_menu_participant_kb

async def build_participant_menu(
    telegram_id: int
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Construct the participant's main menu text and keyboard.
    Fetches the participant and related course info in a single query to avoid DetachedInstanceError.

    Returns:
        text: Formatted overview of balances and course.
        kb: InlineKeyboardMarkup for banking operations.
    """
    # Load participant with related course eagerly
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Participant)
            .options(selectinload(Participant.course))
            .where(
                Participant.telegram_id == telegram_id,
                Participant.is_registered == True
            )
        )
        result = await session.execute(stmt)
        participant = result.scalar_one_or_none()

        if not participant:
            text = "Participant not found or not registered."
            return text, InlineKeyboardMarkup()

        # Capture values while session is open
        name = participant.name
        course_name = participant.course.name
        balance = participant.balance
        savings = participant.savings_balance
        loan = participant.loan_balance

    # Build the display text and keyboard outside session
    text = LEXICON["main_balance_text"].format(
        name=name,
        course_name=course_name,
        balance=balance,
        savings=savings,
        loan=loan
    )
    kb = main_menu_participant_kb()
    return text, kb
