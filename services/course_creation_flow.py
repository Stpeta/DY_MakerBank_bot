from aiogram import types
from aiogram.fsm.context import FSMContext
from states.fsm import CourseCreation
from services.google_sheets import create_course_sheet
from services.course_service import create_course_basic
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
    await message.answer(LEXICON["course_admin_email_request"], parse_mode="HTML",)
    await state.set_state(CourseCreation.waiting_for_admin_email)


async def process_admin_email(message: types.Message, state: FSMContext) -> None:
    email = message.text.strip()

    data = await state.get_data()
    sheet_url = create_course_sheet(data["name"], email)
    course = await create_course_basic(
        name=data["name"],
        description=data["description"],
        creator_id=message.from_user.id,
        sheet_url=sheet_url,
        savings_rate=data.get("savings_rate", 0),
        loan_rate=data.get("loan_rate", 0),
    )

    await message.answer(
        LEXICON["course_created"].format(name=course.name, sheet_url=sheet_url),
        parse_mode="HTML",
    )
    await state.clear()
