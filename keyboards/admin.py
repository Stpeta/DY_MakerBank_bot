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
    """Keyboard under course info allowing full management."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON["button_edit_name"],
                callback_data=f"admin:course:edit:name:{course_id}"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_edit_description"],
                callback_data=f"admin:course:edit:description:{course_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_edit_interest_day"],
                callback_data=f"admin:course:edit:interest_day:{course_id}"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_edit_interest_time"],
                callback_data=f"admin:course:edit:interest_time:{course_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_edit_savings_rate"],
                callback_data=f"admin:course:edit:savings_rate:{course_id}"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_edit_loan_rate"],
                callback_data=f"admin:course:edit:loan_rate:{course_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_edit_max_loan"],
                callback_data=f"admin:course:edit:max_loan:{course_id}"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_edit_savings_lock"],
                callback_data=f"admin:course:edit:savings_lock:{course_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_finish_course"],
                callback_data=f"admin:course:finish:{course_id}"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_back"],
                callback_data="admin:back_to_main"
            ),
        ],
    ])

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
