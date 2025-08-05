# keyboards/admin.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Course
from lexicon.lexicon_en import LEXICON


def main_menu_admin_kb() -> InlineKeyboardMarkup:
    """
    Нижняя строка клавиатуры админа: Только «Новый курс»
    (Кнопка «О боте» убрана — вместо неё команда /about)
    """
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=LEXICON["button_new_course"],
            callback_data="admin:new_course"
        ),
    ]])


def courses_list_kb(courses: list[Course]) -> InlineKeyboardMarkup:
    """
    Список курсов админа, каждая кнопка — отдельная строка
    """
    keyboard = []
    for course in courses:
        emoji = (
            LEXICON["emoji_active"]
            if course.is_active
            else LEXICON["emoji_finished"]
        )
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {course.name}",
                callback_data=f"admin:course:info:{course.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def course_actions_kb(course_id: int) -> InlineKeyboardMarkup:
    """
    Под карточкой курса: «Завершить курс» + «Назад»
    """
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=LEXICON["button_finish_course"],
            callback_data=f"admin:course:finish:{course_id}"
        ),
        InlineKeyboardButton(
            text=LEXICON["button_back"],
            callback_data="admin:back_to_main"
        ),
    ]])

def tx_approval_kb(tx_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for admin to approve or decline a transaction.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON["button_approve"],
                callback_data=f"admin:tx:approve:{tx_id}"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_decline"],
                callback_data=f"admin:tx:decline:{tx_id}"
            ),
        ],
    ])
