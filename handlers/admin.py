# handlers/admin.py

import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from filters.role_filter import RoleFilter
from database.base import AsyncSessionLocal
from database.models import Course
from database.crud import (
    get_course_stats,
    finish_course,
)
from states.fsm import CourseCreation
from services.course_creation_flow import (
    start_course_flow,
    process_course_name,
    process_course_description,
    process_course_sheet,
)
from keyboards.admin import course_actions_kb
from services.admin_menu import build_admin_menu

from services.presenters import render_course_info

from lexicon.lexicon_en import LEXICON

logger = logging.getLogger(__name__)
admin_router = Router()
admin_router.message.filter(RoleFilter("admin"))


@admin_router.message(Command("start"))
async def admin_main(message: Message):
    text, kb = await build_admin_menu(message.from_user.id)
    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data == "admin:back_to_main")
async def admin_back(callback: CallbackQuery):
    await callback.answer()
    text, kb = await build_admin_menu(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith("admin:course:info:"))
async def admin_course_info(callback: CallbackQuery):
    await callback.answer()
    _, _, _, course_id = callback.data.split(":", 3)
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, int(course_id))
        stats  = await get_course_stats(session, course.id)

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
