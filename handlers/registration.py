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


@registration_router.message(Command("start"), RoleFilter("guest"), StateFilter(None))
async def cmd_start(message: Message, state: FSMContext):
    """Start registration for guests via /start."""
    await message.answer(LEXICON["registration_code_request"], parse_mode="HTML")
    await state.set_state(Registration.waiting_for_code)


@registration_router.message(Command("register"), RoleFilter("participant"), StateFilter(None))
async def cmd_register(message: Message, state: FSMContext):
    """Allow existing participants to re-register using /register."""
    await message.answer(LEXICON["registration_code_request"], parse_mode="HTML")
    await state.set_state(Registration.waiting_for_code)


@registration_router.message(Command("start"), RoleFilter("guest"), ~StateFilter(None))
async def start_busy(message: Message):
    """Warn guest to complete current operation before restarting registration."""
    await message.answer(LEXICON["operation_in_progress"], parse_mode="HTML")


@registration_router.message(Command("register"), RoleFilter("participant"), ~StateFilter(None))
async def register_busy(message: Message):
    """Warn participant to complete current operation before re-registering."""
    await message.answer(LEXICON["operation_in_progress"], parse_mode="HTML")


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

    # Successfully registered
    await message.answer(
        LEXICON["registration_success"].format(name=part.name),
        parse_mode="HTML",
    )
    await state.clear()
