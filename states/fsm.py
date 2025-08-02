# states/fsm.py

from aiogram.fsm.state import StatesGroup, State

class CourseCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_sheet = State()  # было waiting_for_csv

class Registration(StatesGroup):
    waiting_for_code = State()
