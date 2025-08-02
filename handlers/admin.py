# handlers/admin.py

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from filters.role_filter import RoleFilter
from states.fsm import CourseCreation
from services.course_flow import (
    start_course_flow,
    process_course_name,
    process_course_description,
    process_course_sheet,
)
from lexicon.lexicon_en import LEXICON

admin_router = Router()
# Фильтруем только админов
admin_router.message.filter(RoleFilter("admin"))

@admin_router.message(Command("new_course"))
async def cmd_new_course(message: Message, state: FSMContext):
    """
    Старт потока создания курса: спрашиваем название.
    """
    await start_course_flow(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_name))
async def handle_course_name(message: Message, state: FSMContext):
    """
    Получили название курса — спрашиваем описание.
    """
    await process_course_name(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_description))
async def handle_course_description(message: Message, state: FSMContext):
    """
    Получили описание курса — спрашиваем ссылку на Google Sheet.
    """
    await process_course_description(message, state)


@admin_router.message(StateFilter(CourseCreation.waiting_for_sheet))
async def handle_course_sheet(message: Message, state: FSMContext):
    """
    Получили URL Google Sheet — обрабатываем и завершаем поток.
    """
    await process_course_sheet(message, state)
