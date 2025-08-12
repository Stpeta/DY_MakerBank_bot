import logging

from aiogram import types
from aiogram.fsm.context import FSMContext
from states.fsm import CourseCreation
from services.google_sheets import is_valid_sheet_url, prepare_course_sheet
from database.crud_courses import create_course, set_rate
from config_data import config
from lexicon.lexicon_en import LEXICON
from database.base import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def start_course_flow(message: types.Message, state: FSMContext) -> None:
    """Initialize the course creation finite state machine."""
    await state.clear()
    await message.answer(LEXICON["course_name_request"], parse_mode="HTML")
    await state.set_state(CourseCreation.waiting_for_name)


async def process_course_name(message: types.Message, state: FSMContext) -> None:
    """Store course name and ask for description."""
    await state.update_data(name=message.text.strip())
    await message.answer(LEXICON["course_description_request"], parse_mode="HTML")
    await state.set_state(CourseCreation.waiting_for_description)


async def process_course_description(message: types.Message, state: FSMContext) -> None:
    """Store course description and ask for savings rate."""
    await state.update_data(description=message.text.strip())
    await message.answer(LEXICON["course_savings_rate_request"], parse_mode="HTML")
    await state.set_state(CourseCreation.waiting_for_savings_rate)


async def process_savings_rate(message: types.Message, state: FSMContext) -> None:
    """Validate and store savings interest rate, then prompt for loan rate."""
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    if rate < 0:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    await state.update_data(savings_rate=rate)
    await message.answer(LEXICON["course_loan_rate_request"], parse_mode="HTML")
    await state.set_state(CourseCreation.waiting_for_loan_rate)


async def process_loan_rate(message: types.Message, state: FSMContext) -> None:
    """Validate and store loan interest rate, then ask for sheet URL."""
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    if rate < 0:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    await state.update_data(loan_rate=rate)
    await message.answer(
        LEXICON["course_sheet_request"].format(email=config.SHEET_EDITOR_EMAIL),
        parse_mode="HTML",
    )
    await state.set_state(CourseCreation.waiting_for_sheet)


async def process_course_sheet(message: types.Message, state: FSMContext) -> None:
    """Validate sheet URL, prepare it, create course, and respond."""
    sheet_url = message.text.strip()
    if not is_valid_sheet_url(sheet_url):
        await message.answer(LEXICON["course_sheet_invalid_format"], parse_mode="HTML")
        return

    try:
        prepare_course_sheet(sheet_url)
    except Exception:  # gspread.exceptions.APIError etc.
        logger.exception("Failed to prepare sheet")
        await message.answer(
            LEXICON["course_sheet_setup_error"].format(
                email=config.SHEET_EDITOR_EMAIL
            ),
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        course = await create_course(
            session,
            name=data["name"],
            description=data["description"],
            creator_id=message.from_user.id,
            sheet_url=sheet_url,
        )
        await set_rate(session, course.id, "savings", data.get("savings_rate", 0))
        await set_rate(session, course.id, "loan", data.get("loan_rate", 0))

    await message.answer(
        LEXICON["course_created"].format(name=course.name),
        parse_mode="HTML",
    )
    await state.clear()
