# handlers/admin.py

import logging
from datetime import datetime

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
from database.crud_transactions import update_transaction_status
from database.crud_participant import adjust_participant_balance
from database.crud_courses import (
    finish_course,
    get_course_stats,
    get_current_rate,
    set_rate,
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
    process_savings_rate,
    process_loan_rate,
    process_admin_email,
)
from services.participant_menu import build_participant_menu
from services.presenters import render_course_info, render_participant_info
from services.google_sheets import update_course_balances
from services.course_service import add_new_participants_from_sheet
from states.fsm import CourseCreation, CourseEdit
from sqlalchemy import select

logger = logging.getLogger(__name__)
admin_router = Router()
admin_router.message.filter(RoleFilter("admin"))


@admin_router.message(Command("start"))
async def admin_main(message: Message):
    text, kb = await build_admin_menu(message.from_user.id)
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


@admin_router.callback_query(F.data.startswith("admin:course:info:"))
async def admin_course_info(callback: CallbackQuery):
    await callback.answer()
    _, _, _, course_id = callback.data.split(":", 3)
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, int(course_id))
        stats = await get_course_stats(session, course.id)
        savings_rate = await get_current_rate(session, course.id, "savings")
        loan_rate = await get_current_rate(session, course.id, "loan")

    text = render_course_info(course, stats, savings_rate, loan_rate)

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
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@admin_router.callback_query(F.data.startswith("admin:course:generate_codes:"))
async def admin_course_generate_codes(callback: CallbackQuery):
    _, _, _, course_id = callback.data.split(":", 3)
    codes = await add_new_participants_from_sheet(int(course_id))
    if codes:
        await callback.answer(
            LEXICON["codes_generated"].format(count=len(codes)),
            show_alert=True,
        )
    else:
        await callback.answer(LEXICON["codes_none"], show_alert=True)


@admin_router.callback_query(F.data.startswith("admin:course:update_sheet:"))
async def admin_course_update_sheet(callback: CallbackQuery):
    _, _, _, course_id = callback.data.split(":", 3)
    await update_course_balances(int(course_id))
    await callback.answer(LEXICON["sheet_updated"])


@admin_router.callback_query(
    F.data.startswith("admin:course:finish:") & ~F.data.contains("finish_confirm")
)
async def admin_course_finish(callback: CallbackQuery):
    await callback.answer()
    _, _, _, course_id = callback.data.split(":", 3)
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, int(course_id))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON["button_finish_course"],
                callback_data=f"admin:course:finish_confirm:{course_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_back"],
                callback_data=f"admin:course:info:{course_id}"
            )
        ],
    ])
    await callback.message.edit_text(
        LEXICON["finish_confirm"].format(name=course.name),
        reply_markup=kb,
    )


@admin_router.callback_query(F.data.startswith("admin:course:finish_confirm:"))
async def admin_course_finish_confirm(callback: CallbackQuery):
    _, _, _, course_id = callback.data.split(":", 3)
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, int(course_id))
        await finish_course(session, course)
        savings_rate = await get_current_rate(session, course.id, "savings")
        loan_rate = await get_current_rate(session, course.id, "loan")
        result = await session.execute(
            select(Participant).where(
                Participant.course_id == course.id,
                Participant.is_registered,
                Participant.telegram_id.is_not(None),
            )
        )
        participants = result.scalars().all()

    for participant in participants:
        await callback.bot.send_message(
            participant.telegram_id,
            LEXICON["finish_participant_notify"].format(name=course.name),
            parse_mode="HTML",
        )
        balance_text = render_participant_info(
            participant.name,
            course.name,
            participant.balance,
            participant.savings_balance,
            participant.loan_balance,
            savings_rate,
            loan_rate,
        )
        await callback.bot.send_message(
            participant.telegram_id,
            balance_text,
            parse_mode="HTML",
        )

    text, kb = await build_admin_menu(callback.from_user.id)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer(LEXICON["finish_success"].format(name=course.name))
 

# region --- Editing course parameters ---


async def _send_course_info(message: Message, course_id: int) -> None:
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        stats = await get_course_stats(session, course.id)
        savings_rate = await get_current_rate(session, course.id, "savings")
        loan_rate = await get_current_rate(session, course.id, "loan")

    text = render_course_info(course, stats, savings_rate, loan_rate)
    if course.is_active:
        kb = course_actions_kb(course.id)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text=LEXICON["button_back"], callback_data="admin:back_to_main")]])

    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith("admin:course:edit:"))
async def admin_course_edit_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, _, _, field, course_id = callback.data.split(":", 4)
    prompts = {
        "name": "course_name_request",
        "description": "course_description_request",
        "interest_day": "course_interest_day_request",
        "interest_time": "course_interest_time_request",
        "savings_rate": "course_savings_rate_request",
        "loan_rate": "course_loan_rate_request",
        "max_loan": "course_max_loan_request",
        "savings_lock": "course_savings_lock_request",
    }
    states_map = {
        "name": CourseEdit.waiting_for_name,
        "description": CourseEdit.waiting_for_description,
        "interest_day": CourseEdit.waiting_for_interest_day,
        "interest_time": CourseEdit.waiting_for_interest_time,
        "savings_rate": CourseEdit.waiting_for_savings_rate,
        "loan_rate": CourseEdit.waiting_for_loan_rate,
        "max_loan": CourseEdit.waiting_for_max_loan,
        "savings_lock": CourseEdit.waiting_for_savings_lock,
    }
    if field not in prompts:
        return
    await state.update_data(course_id=int(course_id))
    await callback.message.answer(LEXICON[prompts[field]], parse_mode="HTML")
    await state.set_state(states_map[field])


@admin_router.message(StateFilter(CourseEdit.waiting_for_name))
async def edit_course_name(message: Message, state: FSMContext):
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        course.name = message.text.strip()
        await session.commit()
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_description))
async def edit_course_description(message: Message, state: FSMContext):
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        course.description = message.text.strip()
        await session.commit()
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_interest_day))
async def edit_course_interest_day(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer(LEXICON["course_value_invalid"], parse_mode="HTML")
        return
    day = int(text)
    if day < 0 or day > 6:
        await message.answer(LEXICON["course_value_invalid"], parse_mode="HTML")
        return
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        course.interest_day = day
        await session.commit()
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_interest_time))
async def edit_course_interest_time(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        datetime.strptime(text, "%H:%M")
    except ValueError:
        await message.answer(LEXICON["course_value_invalid"], parse_mode="HTML")
        return
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        course.interest_time = text
        await session.commit()
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_savings_rate))
async def edit_course_savings_rate(message: Message, state: FSMContext):
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        await set_rate(session, course_id, "savings", rate)
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_loan_rate))
async def edit_course_loan_rate(message: Message, state: FSMContext):
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        await set_rate(session, course_id, "loan", rate)
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_max_loan))
async def edit_course_max_loan(message: Message, state: FSMContext):
    text = message.text.replace(",", ".").strip()
    try:
        amount = float(text)
    except ValueError:
        await message.answer(LEXICON["course_value_invalid"], parse_mode="HTML")
        return
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        course.max_loan_amount = amount
        await session.commit()
    await state.clear()
    await _send_course_info(message, course_id)


@admin_router.message(StateFilter(CourseEdit.waiting_for_savings_lock))
async def edit_course_savings_lock(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        days = int(text)
    except ValueError:
        await message.answer(LEXICON["course_value_invalid"], parse_mode="HTML")
        return
    data = await state.get_data()
    course_id = data["course_id"]
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        course.savings_withdrawal_delay = days
        await session.commit()
    await state.clear()
    await _send_course_info(message, course_id)


# endregion --- Editing course parameters ---


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


@admin_router.message(StateFilter(CourseCreation.waiting_for_savings_rate))
async def handle_course_savings_rate(message: Message, state: FSMContext):
    await process_savings_rate(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_loan_rate))
async def handle_course_loan_rate(message: Message, state: FSMContext):
    await process_loan_rate(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_admin_email))
async def handle_admin_email(message: Message, state: FSMContext):
    await process_admin_email(message, state)


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
        course = await session.get(Course, participant.course_id)
        course_name = course.name
        if tx.type == "cash_deposit":
            await adjust_participant_balance(session, participant, tx.amount)
        elif tx.type == "cash_withdrawal":
            await adjust_participant_balance(session, participant, -tx.amount)

    # Notify the participant
    if tx.type == "cash_deposit":
        text = LEXICON["deposit_approved"].format(
            amount=tx.amount,
            tx_id=tx_id,
            course_name=course_name,
            name=participant.name)
    else:
        text = LEXICON["withdraw_approved"].format(
            amount=tx.amount,
            tx_id=tx_id,
            course_name=course_name,
            name=participant.name)
    await callback.bot.send_message(participant.telegram_id, text, parse_mode="HTML",)

    # Build the participant menu and send it
    menu_text, menu_kb = await build_participant_menu(
        participant.id, participant.name, course_name
    )
    await callback.bot.send_message(participant.telegram_id, menu_text, parse_mode="HTML", reply_markup=menu_kb)

    # Mark the admin’s notification as handled
    await callback.message.edit_text(
        (
            f"{callback.message.text}\n\n"
            f"{LEXICON['admin_tx_approved_admin'].format(tx_id=tx_id, course_name=course_name, name=participant.name)}"
        ),
        parse_mode="HTML",
        reply_markup=None,
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
        course = await session.get(Course, participant.course_id)
        course_name = course.name

    # Notify the participant
    if tx.type == "cash_deposit":
        text = LEXICON["deposit_declined"].format(
            amount=tx.amount,
            tx_id=tx_id,
            course_name=course_name,
            name=participant.name)
    else:
        text = LEXICON["withdraw_declined"].format(
            amount=tx.amount,
            tx_id=tx_id,
            course_name=course_name,
            name=participant.name)
    await callback.bot.send_message(participant.telegram_id, text, parse_mode="HTML")

    # Build the participant menu and send it
    menu_text, menu_kb = await build_participant_menu(
        participant.id, participant.name, course_name
    )
    await callback.bot.send_message(participant.telegram_id, menu_text, parse_mode="HTML", reply_markup=menu_kb)

    # Mark the admin’s notification as handled
    await callback.message.edit_text(
        (
            f"{callback.message.text}\n\n"
            f"{LEXICON['admin_tx_declined_admin'].format(tx_id=tx_id, course_name=course_name, name=participant.name)}"
        ),
        parse_mode="HTML",
        reply_markup=None,
    )

# endregion --- Approving/Declining Withdrawal/Deposit Requests ---

