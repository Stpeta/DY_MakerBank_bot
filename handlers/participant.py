import logging

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.base import AsyncSessionLocal
from database.crud_participant import get_participants_by_telegram_id

from filters.role_filter import RoleFilter
from keyboards.admin import tx_approval_kb
from keyboards.participant import (
    main_menu_participant_kb,
    cancel_operation_kb,
    select_course_kb,
)

from lexicon.lexicon_en import LEXICON
from services.banking import (
    create_withdrawal_request,
    create_deposit_request,
    cancel_transaction,
)
from services.notifications import send_message_to_course_creator
from services.participant_menu import build_participant_menu
from states.fsm import CashOperations

logger = logging.getLogger(__name__)
participant_router = Router()
participant_router.message.filter(RoleFilter("participant"))
participant_router.callback_query.filter(RoleFilter("participant"))


@participant_router.message(Command("start"))
async def participant_main(message: Message, state: FSMContext):
    """Entry point for participant. Select course if needed."""
    await state.clear()
    async with AsyncSessionLocal() as session:
        participants = await get_participants_by_telegram_id(
            session, message.from_user.id
        )
    if not participants:
        await message.answer("No courses found.")
        return
    if len(participants) == 1:
        p = participants[0]
        await state.set_data(
            {
                "participant_id": p.id,
                "participant_name": p.name,
                "course_id": p.course_id,
                "course_name": p.course.name,
            }
        )
        text, kb = await build_participant_menu(p.id, p.name, p.course.name)
        await message.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        courses = [(p.id, p.course.name) for p in participants]
        data = {
            str(p.id): {
                "participant_name": p.name,
                "course_id": p.course_id,
                "course_name": p.course.name,
            }
            for p in participants
        }
        await state.set_data({"participants": data})
        await message.answer(
            LEXICON["choose_course_prompt"],
            reply_markup=select_course_kb(courses),
        )


@participant_router.callback_query(F.data.startswith("participant:choose_course:"))
async def choose_course(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, _, pid = callback.data.split(":", 2)
    data = await state.get_data()
    info = data.get("participants", {}).get(pid)
    if not info:
        await callback.message.edit_text("Course not found")
        return
    await state.set_data(
        {
            "participant_id": int(pid),
            "participant_name": info["participant_name"],
            "course_id": info["course_id"],
            "course_name": info["course_name"],
        }
    )
    text, kb = await build_participant_menu(
        int(pid), info["participant_name"], info["course_name"]
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


# region --- Withdraw Flow ---

@participant_router.callback_query(F.data == "participant:withdraw_cash")
async def ask_withdraw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["withdraw_amount_request"],
        parse_mode="HTML",
        reply_markup=cancel_operation_kb()
    )
    await state.set_state(CashOperations.waiting_for_withdraw_amount)


@participant_router.message(StateFilter(CashOperations.waiting_for_withdraw_amount))
async def process_withdraw(message: Message, state: FSMContext):
    # Handle withdrawal amount, create pending request, notify admin, await approval.
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        return await message.answer(
            LEXICON["invalid_amount"],
            parse_mode="HTML",
            reply_markup=cancel_operation_kb()
        )
    amount = int(text)

    # Create pending transaction
    data = await state.get_data()
    if data.get("participant_id") is None:
        return
    try:
        tx_id = await create_withdrawal_request(data.get("participant_id"), amount)
    except ValueError as e:
        return await message.answer(
            str(e),
            parse_mode="HTML",
            reply_markup=cancel_operation_kb()
        )

    course_id = data.get("course_id")
    course_name = data.get("course_name")
    participant_name = data.get("participant_name")

    # Notify the course creator (admin)
    await send_message_to_course_creator(
        bot=message.bot,
        course_id=course_id,
        text=LEXICON["admin_withdraw_request"].format(
            course_name=course_name,
            name=participant_name,
            amount=amount,
            tx_id=tx_id
        ),
        reply_markup=tx_approval_kb(tx_id)
    )

    # Move to approval-wait state
    await state.update_data(tx_id=tx_id)
    await state.set_state(CashOperations.waiting_for_approval)

    await message.answer(
        LEXICON["withdraw_waiting_approval"].format(amount=amount,tx_id=tx_id),
        parse_mode="HTML",
        reply_markup=cancel_operation_kb()
    )


# endregion --- Withdraw Flow ---

# region --- Deposit Flow ---

@participant_router.callback_query(F.data == "participant:deposit_cash")
async def ask_deposit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["deposit_amount_request"],
        parse_mode="HTML",
        reply_markup=cancel_operation_kb()
    )
    await state.set_state(CashOperations.waiting_for_deposit_amount)


@participant_router.message(StateFilter(CashOperations.waiting_for_deposit_amount))
async def process_deposit(message: Message, state: FSMContext):
    """Handle deposit amount, create pending request, notify admin, await approval."""
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        return await message.answer(
            LEXICON["invalid_amount"],
            parse_mode="HTML",
            reply_markup=cancel_operation_kb()
        )
    amount = int(text)

    # Create pending transaction
    data = await state.get_data()
    pid = data.get("participant_id")
    if pid is None:
        return
    try:
        tx_id = await create_deposit_request(pid, amount)
    except ValueError as e:
        return await message.answer(
            str(e),
            parse_mode="HTML",
            reply_markup=main_menu_participant_kb()
        )

    course_id = data.get("course_id")
    course_name = data.get("course_name")
    participant_name = data.get("participant_name")

    # Notify the course creator (admin)
    await send_message_to_course_creator(
        bot=message.bot,
        course_id=course_id,
        text=LEXICON["admin_deposit_request"].format(
            course_name=course_name,
            name=participant_name,
            amount=amount,
            tx_id=tx_id
        ),
        reply_markup=tx_approval_kb(tx_id)
    )

    # Move to approval-wait state
    await state.update_data(tx_id=tx_id)
    await state.set_state(CashOperations.waiting_for_approval)

    await message.answer(
        LEXICON["deposit_waiting_approval"].format(amount=amount, tx_id=tx_id),
        parse_mode="HTML",
        reply_markup=cancel_operation_kb()
    )

# endregion --- Deposit Flow ---

# region --- Withdraw/Deposit Cancellation ---

@participant_router.callback_query(
    F.data == "participant:cancel",
    StateFilter(CashOperations.waiting_for_approval)
)
async def user_cancel_withdraw(callback: CallbackQuery, state: FSMContext):
    """Allow user to cancel their own pending transaction."""
    data = await state.get_data()
    tx_id = data.pop("tx_id", None)
    pid = data.get("participant_id")
    participant_name = data.get("participant_name")
    course_name = data.get("course_name")
    if tx_id and pid:
        await cancel_transaction(pid, tx_id)

    await state.set_state(None)
    await state.set_data(data)
    text, kb = await build_participant_menu(pid, participant_name, course_name)
    await callback.message.edit_text(
        LEXICON["withdraw_cancelled"],
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


@participant_router.callback_query(
    F.data == "participant:cancel",
    StateFilter(CashOperations.waiting_for_withdraw_amount)
)
async def cancel_during_withdraw(callback: CallbackQuery, state: FSMContext):
    """Cancel withdrawal before submitting amount."""
    await callback.answer()  # remove loading
    data = await state.get_data()
    await state.set_state(None)
    text, kb = await build_participant_menu(
        data.get("participant_id"), data.get("participant_name"), data.get("course_name")
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@participant_router.callback_query(
    F.data == "participant:cancel",
    StateFilter(CashOperations.waiting_for_deposit_amount)
)
async def cancel_during_deposit(callback: CallbackQuery, state: FSMContext):
    """Cancel deposit before submitting amount."""
    await callback.answer()
    data = await state.get_data()
    await state.set_state(None)
    text, kb = await build_participant_menu(
        data.get("participant_id"), data.get("participant_name"), data.get("course_name")
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

# endregion --- Withdraw/Deposit Cancellation ---
