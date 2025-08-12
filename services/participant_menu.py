from aiogram.types import InlineKeyboardMarkup

from database.base import AsyncSessionLocal
from database.models import Participant
from database.crud_courses import get_current_rate

from keyboards.participant import main_menu_participant_kb

from services.presenters import render_participant_info


async def build_participant_menu(
        participant_id: int,
        participant_name: str,
        course_name: str,
) -> tuple[str, InlineKeyboardMarkup]:
    """Construct main menu text and keyboard for a participant."""
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        if not participant:
            text = "Participant not found or not registered."
            return text, InlineKeyboardMarkup()
        wallet = participant.wallet_balance
        savings = participant.savings_balance
        loan = participant.loan_balance
        savings_rate = await get_current_rate(session, participant.course_id, "savings")
        loan_rate = await get_current_rate(session, participant.course_id, "loan")

    text = render_participant_info(
        participant_name,
        course_name,
        wallet,
        savings,
        loan,
        savings_rate,
        loan_rate,
    )
    kb = main_menu_participant_kb()
    return text, kb
