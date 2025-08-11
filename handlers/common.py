from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from lexicon.lexicon_en import LEXICON

common_router = Router()

@common_router.message(Command("about"))
async def cmd_about(message: Message):
    """Generic handler for /about — works for any user."""
    await message.answer(LEXICON["about_text"], parse_mode="HTML")
