# states/fsm.py

from aiogram.fsm.state import StatesGroup, State

class CourseCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_sheet = State()

class Registration(StatesGroup):
    waiting_for_code = State()

class CourseFinish(StatesGroup):
    waiting_for_course = State()