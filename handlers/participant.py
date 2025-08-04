from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.role_filter import RoleFilter
from lexicon.lexicon_en import LEXICON
from keyboards.participant import main_menu_participant_kb

participant_router = Router()
participant_router.message.filter(RoleFilter("participant"))

@participant_router.message(Command("start"))
async def participant_start(message: Message):
    await message.answer(
        LEXICON["participant_greeting"],
        reply_markup=main_menu_participant_kb()
    )

