from aiogram import types
from aiogram.fsm.context import FSMContext
from states.fsm import CourseCreation
from services.course_service import create_course
from lexicon.lexicon_en import LEXICON


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
    await state.update_data(savings_rate=rate)
    await message.answer(LEXICON["course_loan_rate_request"], parse_mode="HTML")
    await state.set_state(CourseCreation.waiting_for_loan_rate)


async def process_loan_rate(message: types.Message, state: FSMContext) -> None:
    """Validate loan interest rate and create the course with a spreadsheet."""
    text = message.text.replace(",", ".").strip()
    try:
        rate = float(text)
    except ValueError:
        await message.answer(LEXICON["course_rate_invalid"], parse_mode="HTML")
        return
    await state.update_data(loan_rate=rate)

    data = await state.get_data()
    try:
        course = await create_course(
            name=data["name"],
            description=data["description"],
            creator_id=message.from_user.id,
            savings_rate=data.get("savings_rate", 0),
            loan_rate=data.get("loan_rate", 0),
        )
    except Exception:
        await message.answer(LEXICON["sheet_creation_failed"], parse_mode="HTML")
        await state.clear()
        return

    await message.answer(
        LEXICON["course_sheet_created"].format(
            name=course.name, url=course.sheet_url
        ),
        parse_mode="HTML",
    )
    await state.clear()
