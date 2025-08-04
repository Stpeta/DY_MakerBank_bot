# handlers/guest.py

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.role_filter import RoleFilter
from states.fsm import Registration
from services.participant_registration import register_by_code
from lexicon.lexicon_en import LEXICON

guest_router = Router()
guest_router.message.filter(RoleFilter("guest"))


@guest_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(LEXICON["registration_welcome"])


@guest_router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    await message.answer(LEXICON["registration_code_request"])
    await state.set_state(Registration.waiting_for_code)


@guest_router.message(StateFilter(Registration.waiting_for_code))
async def process_registration_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    part, status = await register_by_code(code, message.from_user.id)

    if status == "not_found":
        await message.answer(LEXICON["registration_not_found"])
        return
    if status == "already":
        await message.answer(LEXICON["registration_already"].format(name=part.name))
        await state.clear()
        return

    # Успешно
    await message.answer(LEXICON["registration_success"].format(name=part.name))
    await state.clear()
