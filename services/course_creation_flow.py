from aiogram import types
from aiogram.fsm.context import FSMContext
from states.fsm import CourseCreation
from services.google_sheets import (
    is_valid_sheet_url,
    fetch_students,
    write_registration_codes,
)
from services.course_service import create_course_with_participants
from lexicon.lexicon_en import LEXICON


async def start_course_flow(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(LEXICON["course_name_request"], parse_mode="HTML",)
    await state.set_state(CourseCreation.waiting_for_name)


async def process_course_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await message.answer(LEXICON["course_description_request"], parse_mode="HTML",)
    await state.set_state(CourseCreation.waiting_for_description)


async def process_course_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip())
    await message.answer(LEXICON["course_savings_rate_request"], parse_mode="HTML",)
    await state.set_state(CourseCreation.waiting_for_savings_rate)


async def process_savings_rate(message: types.Message, state: FSMContext) -> None:
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML",)
        return
    await state.update_data(savings_rate=rate)
    await message.answer(LEXICON["course_loan_rate_request"], parse_mode="HTML",)
    await state.set_state(CourseCreation.waiting_for_loan_rate)


async def process_loan_rate(message: types.Message, state: FSMContext) -> None:
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML",)
        return
    await state.update_data(loan_rate=rate)
    await message.answer(LEXICON["course_sheet_request"], parse_mode="HTML",)
    await state.set_state(CourseCreation.waiting_for_sheet)


async def process_course_sheet(message: types.Message, state: FSMContext) -> None:
    sheet_url = message.text.strip()
    if not is_valid_sheet_url(sheet_url):
        await message.answer(LEXICON["course_sheet_invalid_format"], parse_mode="HTML",)
        return

    # 1) читаем участников
    try:
        participants_raw = fetch_students(sheet_url)
    except Exception:  # gspread.exceptions.APIError и др.
        await message.answer(LEXICON["course_sheet_unreachable"], parse_mode="HTML",)
        return

    if not participants_raw:
        await message.answer(LEXICON["course_sheet_empty"], parse_mode="HTML",)
        return

    # 2) сервис создаёт курс и возвращает карту кодов
    data = await state.get_data()
    course, codes_map = await create_course_with_participants(
        name=data["name"],
        description=data["description"],
        creator_id=message.from_user.id,
        sheet_url=sheet_url,
        participants_raw=participants_raw,
        savings_rate=data.get("savings_rate", 0),
        loan_rate=data.get("loan_rate", 0),
    )

    # 3) пишем коды обратно в Google Sheet
    write_registration_codes(sheet_url, codes_map)

    # 4) финальный ответ
    await message.answer(
        LEXICON["course_created"].format(name=course.name, count=len(codes_map)),
        parse_mode="HTML",
    )
    await state.clear()
