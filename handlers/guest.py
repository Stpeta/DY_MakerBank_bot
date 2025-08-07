from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.role_filter import RoleFilter
from keyboards.participant import main_menu_participant_kb
from lexicon.lexicon_en import LEXICON
from services.participant_registration import register_by_code
from states.fsm import Registration

# Router for guest users
guest_router = Router()
guest_router.message.filter(RoleFilter("guest"))


@guest_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Prompt guest to enter registration code at start."""
    await message.answer(LEXICON["registration_code_request"], parse_mode="HTML",)
    await state.set_state(Registration.waiting_for_code)


@guest_router.message(StateFilter(Registration.waiting_for_code))
async def process_registration_code(message: Message, state: FSMContext):
    """Process entered code, register participant."""
    code = message.text.strip().upper()

    try:
        part, status = await register_by_code(code, message.from_user.id)
    except Exception as e:
        print(f"[REGISTRATION ERROR] code={code}, err={e}")
        await message.answer(
            LEXICON.get("registration_error", "Registration error. Try again later."),
            parse_mode="HTML",
        )
        await state.clear()
        return

    if status == "not_found":
        await message.answer(LEXICON["registration_not_found"], parse_mode="HTML",)
        await state.clear()
        return

    if status == "already":
        await message.answer(
            LEXICON["registration_already"].format(name=part.name),
            parse_mode="HTML",
        )
        await state.clear()
        return

    # Успешно зарегистрирован
    await message.answer(
        LEXICON["registration_success"].format(name=part.name),
        parse_mode="HTML",
    )
    await message.answer(
        "Now you can use /start to access your banking menu.",
        parse_mode="HTML",
    )
    await state.clear()
