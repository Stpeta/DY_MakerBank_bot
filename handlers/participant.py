import logging

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.base import AsyncSessionLocal
from database.crud import get_participant_by_telegram_id
from filters.role_filter import RoleFilter
from keyboards.admin import tx_approval_kb
from keyboards.participant import main_menu_participant_kb, cancel_operation_kb
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
async def participant_main(message: Message):
    """Show participant’s main banking menu."""
    text, kb = await build_participant_menu(message.from_user.id)
    await message.answer(text, reply_markup=kb)


# region --- Withdraw Flow ---

@participant_router.callback_query(F.data == "participant:withdraw_cash")
async def ask_withdraw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["withdraw_amount_request"],
        reply_markup=cancel_operation_kb()
    )
    await state.set_state(CashOperations.waiting_for_withdraw_amount)


@participant_router.message(StateFilter(CashOperations.waiting_for_withdraw_amount))
async def process_withdraw(message: Message, state: FSMContext):
    """Handle withdrawal amount, create pending request, notify admin, await approval."""
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        return await message.answer(
            LEXICON["invalid_amount"],
            reply_markup=cancel_operation_kb()
        )
    amount = int(text)

    # Create pending transaction
    try:
        tx_id = await create_withdrawal_request(message.from_user.id, amount)
    except ValueError as e:
        return await message.answer(
            str(e),
            reply_markup=main_menu_participant_kb()
        )

    # Lookup participant to get course_id
    async with AsyncSessionLocal() as session:
        participant = await get_participant_by_telegram_id(session, message.from_user.id)
        course_id = participant.course_id

    # Notify the course creator (admin)
    await send_message_to_course_creator(
        bot=message.bot,
        course_id=course_id,
        text=LEXICON["admin_withdraw_request"].format(
            name=participant.name,
            amount=amount,
            tx_id=tx_id
        ),
        reply_markup=tx_approval_kb(tx_id)
    )

    # Move to approval-wait state
    await state.update_data(tx_id=tx_id)
    await state.set_state(CashOperations.waiting_for_approval)

    await message.answer(
        LEXICON["withdraw_waiting_approval"].format(amount=amount),
        reply_markup=cancel_operation_kb()
    )


# endregion --- Withdraw Flow ---

# region --- Deposit Flow ---

@participant_router.callback_query(F.data == "participant:deposit_cash")
async def ask_deposit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["deposit_amount_request"],
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
            reply_markup=cancel_operation_kb()
        )
    amount = int(text)

    # Create pending transaction
    try:
        tx_id = await create_deposit_request(message.from_user.id, amount)
    except ValueError as e:
        return await message.answer(
            str(e),
            reply_markup=main_menu_participant_kb()
        )

    # Lookup participant to get course_id
    async with AsyncSessionLocal() as session:
        participant = await get_participant_by_telegram_id(session, message.from_user.id)
        course_id = participant.course_id

    # Notify the course creator (admin)
    await send_message_to_course_creator(
        bot=message.bot,
        course_id=course_id,
        text=LEXICON["admin_deposit_request"].format(
            name=participant.name,
            amount=amount,
            tx_id=tx_id
        ),
        reply_markup=tx_approval_kb(tx_id)
    )

    # Move to approval-wait state
    await state.update_data(tx_id=tx_id)
    await state.set_state(CashOperations.waiting_for_approval)

    await message.answer(
        LEXICON["deposit_waiting_approval"].format(amount=amount),
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
    tx_id = data.get("tx_id")
    if tx_id:
        await cancel_transaction(callback.from_user.id, tx_id)

    await state.clear()
    text, kb = await build_participant_menu(callback.from_user.id)
    await callback.message.edit_text(
        LEXICON["withdraw_cancelled"],
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
    await state.clear()  # reset FSM

    # Rebuild and show main menu
    text, kb = await build_participant_menu(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb)


@participant_router.callback_query(
    F.data == "participant:cancel",
    StateFilter(CashOperations.waiting_for_deposit_amount)
)
async def cancel_during_deposit(callback: CallbackQuery, state: FSMContext):
    """Cancel deposit before submitting amount."""
    await callback.answer()
    await state.clear()

    text, kb = await build_participant_menu(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb)

# endregion --- Withdraw/Deposit Cancellation ---
