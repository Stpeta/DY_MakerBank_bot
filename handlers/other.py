from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from filters.role_filter import RoleFilter
from states.fsm import Registration
from services.courses import register_by_code
from lexicon.lexicon_en import LEXICON

other_router = Router()
other_router.message.filter(RoleFilter("other"))

@other_router.message(Command("register"))
async def cmd_register(message: Message):
    await message.answer(LEXICON["registration_code_request"])
    await Registration.waiting_for_code.set()