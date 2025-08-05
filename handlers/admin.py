# handlers/admin.py

import logging

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from database.base import AsyncSessionLocal
from database.crud import (
    get_course_stats,
    finish_course,
    update_transaction_status,
    adjust_participant_balance,
)
from database.models import Course, Transaction, Participant
from filters.role_filter import RoleFilter
from keyboards.admin import course_actions_kb
from lexicon.lexicon_en import LEXICON
from services.admin_menu import build_admin_menu
from services.course_creation_flow import (
    start_course_flow,
    process_course_name,
    process_course_description,
    process_course_sheet,
)
from services.presenters import render_course_info
from states.fsm import CourseCreation

logger = logging.getLogger(__name__)
admin_router = Router()
admin_router.message.filter(RoleFilter("admin"))


@admin_router.message(Command("start"))
async def admin_main(message: Message):
    text, kb = await build_admin_menu(message.from_user.id)
    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith("admin:course:info:"))
async def admin_course_info(callback: CallbackQuery):
    await callback.answer()
    _, _, _, course_id = callback.data.split(":", 3)
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, int(course_id))
        stats = await get_course_stats(session, course.id)

    text = render_course_info(course, stats)

    if course.is_active:
        kb = course_actions_kb(course.id)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=LEXICON["button_back"],
                callback_data="admin:back_to_main"
            )
        ]])

    await callback.message.edit_text(text, reply_markup=kb)


@admin_router.callback_query(F.data == "admin:back_to_main")
async def admin_back(callback: CallbackQuery):
    await callback.answer()
    text, kb = await build_admin_menu(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith("admin:course:finish:"))
async def admin_course_finish(callback: CallbackQuery):
    await callback.answer()
    _, _, _, course_id = callback.data.split(":", 3)
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, int(course_id))
        await finish_course(session, course)

    # после завершения возвращаем главное меню одним edit
    text, kb = await build_admin_menu(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb)


# region --- FSM для /new_course ---

@admin_router.callback_query(F.data == "admin:new_course")
async def admin_new_course(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_course_flow(callback.message, state)


@admin_router.message(Command("new_course"))
async def cmd_new_course(message: Message, state: FSMContext):
    await start_course_flow(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_name))
async def handle_course_name(message: Message, state: FSMContext):
    await process_course_name(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_description))
async def handle_course_description(message: Message, state: FSMContext):
    await process_course_description(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_sheet))
async def handle_course_sheet(message: Message, state: FSMContext):
    await process_course_sheet(message, state)


# endregion --- FSM для /new_course ---

# region --- Approving/Declining Withdrawal/Deposit Requests ---

@admin_router.callback_query(F.data.startswith("admin:tx:approve:"))
async def admin_tx_approve(callback: CallbackQuery):
    await callback.answer()
    _, _, _, tx_id_str = callback.data.split(":", 3)
    tx_id = int(tx_id_str)

    async with AsyncSessionLocal() as session:
        tx = await session.get(Transaction, tx_id)
        if not tx or tx.status != "pending":
            return

        # Approve the transaction
        await update_transaction_status(session, tx, "completed")

        # Apply balance change
        participant = await session.get(Participant, tx.participant_id)
        if tx.type == "cash_deposit":
            await adjust_participant_balance(session, participant, tx.amount)
        elif tx.type == "cash_withdrawal":
            await adjust_participant_balance(session, participant, -tx.amount)

    # Notify the participant
    if tx.type == "cash_deposit":
        text = LEXICON["deposit_approved"].format(amount=tx.amount)
    else:
        text = LEXICON["withdraw_approved"].format(amount=tx.amount)
    await callback.bot.send_message(participant.telegram_id, text)

    # Update the admin’s notification message to show it’s handled
    await callback.message.edit_text(
        f"{callback.message.text}\n\nTransaction {tx_id} approved.",
        reply_markup=None
    )


@admin_router.callback_query(F.data.startswith("admin:tx:decline:"))
async def admin_tx_decline(callback: CallbackQuery):
    await callback.answer()
    _, _, _, tx_id_str = callback.data.split(":", 3)
    tx_id = int(tx_id_str)

    async with AsyncSessionLocal() as session:
        tx = await session.get(Transaction, tx_id)
        if not tx or tx.status != "pending":
            return

        # Decline the transaction
        await update_transaction_status(session, tx, "declined")
        participant = await session.get(Participant, tx.participant_id)

    # Notify the participant
    if tx.type == "cash_deposit":
        text = LEXICON["deposit_declined"].format(amount=tx.amount)
    else:
        text = LEXICON["withdraw_declined"].format(amount=tx.amount)
    await callback.bot.send_message(participant.telegram_id, text)

    # Mark the admin’s notification as handled
    await callback.message.edit_text(
        f"{callback.message.text}\n\nTransaction {tx_id} declined.",
        reply_markup=None
    )

# endregion --- Approving/Declining Withdrawal/Deposit Requests ---
