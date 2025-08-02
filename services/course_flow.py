from aiogram import types
from aiogram.fsm.context import FSMContext
from states.fsm import CourseCreation
from services.google_sheets import fetch_students, write_registration_codes
from services.courses import _gen_code
from database.crud import create_course, add_participants
from database.base import AsyncSessionLocal
from lexicon.lexicon_en import LEXICON

async def start_course_flow(message: types.Message, state: FSMContext) -> None:
    # Запросить название курса
    await state.clear()
    await message.answer(LEXICON["course_name_request"])
    await state.set_state(CourseCreation.waiting_for_name)

async def process_course_name(message: types.Message, state: FSMContext) -> None:
    # Сохранить название и спросить описание
    await state.update_data(name=message.text)
    await message.answer(LEXICON["course_description_request"])
    await state.set_state(CourseCreation.waiting_for_description)

async def process_course_description(message: types.Message, state: FSMContext) -> None:
    # Сохранить описание и попросить ссылку на Google Sheet
    await state.update_data(description=message.text)
    await message.answer(LEXICON["course_sheet_request"])
    await state.set_state(CourseCreation.waiting_for_sheet)

async def process_course_sheet(message: types.Message, state: FSMContext) -> None:
    # Получаем URL и сохраняем в FSM
    sheet_url = message.text.strip()
    await state.update_data(sheet_url=sheet_url)

    # Читаем участников из Google Sheets
    participants_raw = fetch_students(sheet_url)
    if not participants_raw:
        await message.answer(LEXICON["course_sheet_invalid"])
        return

    # Генерация кодов
    existing = set()
    participants = []
    codes_map = {}
    for name, email in participants_raw:
        code = _gen_code(existing)
        existing.add(code)
        participants.append({
            "name": name,
            "email": email,
            "registration_code": code
        })
        codes_map[email] = code

    # Сохраняем в БД, включая sheet_url
    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        course = await create_course(
            session,
            name=data["name"],
            description=data["description"],
            creator_id=message.from_user.id,
            sheet_url=sheet_url           # ← передаём сюда
        )
        await add_participants(session, course.id, participants)

    # Записываем коды обратно в таблицу
    write_registration_codes(sheet_url, codes_map)

    # Подтверждаем создание
    await message.answer(
        LEXICON["course_created"].format(
            name=course.name,
            count=len(participants)
        )
    )
    await state.clear()