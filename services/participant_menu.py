from aiogram.types import InlineKeyboardMarkup

from database.base import AsyncSessionLocal
from database.models import Participant

from keyboards.participant import main_menu_participant_kb

from lexicon.lexicon_en import LEXICON


async def build_participant_menu(
        participant_id: int,
        participant_name: str,
        course_name: str,
) -> tuple[str, InlineKeyboardMarkup]:
    # Construct main menu text and keyboard for a participant
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        if not participant:
            text = "Participant not found or not registered."
            return text, InlineKeyboardMarkup()

        balance = participant.balance
        savings = participant.savings_balance
        loan = participant.loan_balance

    text = LEXICON["main_balance_text"].format(
        name=participant_name,
        course_name=course_name,
        balance=balance,
        savings=savings,
        loan=loan
    )
    kb = main_menu_participant_kb()
    return text, kb
