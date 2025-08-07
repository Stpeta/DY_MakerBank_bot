from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.role_filter import RoleFilter
from lexicon.lexicon_en import LEXICON
from services.participant_registration import register_by_code
from states.fsm import Registration

# Router for registration flows
registration_router = Router()


@registration_router.message(Command("start"), RoleFilter("guest"))
async def cmd_start(message: Message, state: FSMContext):
    """Start registration for guests via /start."""
    await message.answer(LEXICON["registration_code_request"], parse_mode="HTML")
    await state.set_state(Registration.waiting_for_code)


@registration_router.message(Command("register"), RoleFilter("participant"))
async def cmd_register(message: Message, state: FSMContext):
    """Allow existing participants to re-register using /register."""
    await message.answer(LEXICON["registration_code_request"], parse_mode="HTML")
    await state.set_state(Registration.waiting_for_code)


@registration_router.message(StateFilter(Registration.waiting_for_code))
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
