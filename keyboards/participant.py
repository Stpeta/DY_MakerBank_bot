# keyboards/participant.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lexicon.lexicon_en import LEXICON

def main_menu_participant_kb() -> InlineKeyboardMarkup:
    """
    Inline-клавиатура участника: Баланс, Пополнить, Вывести, Регистрация
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON["button_balance"],
                callback_data="participant:balance"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_deposit"],
                callback_data="participant:deposit"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_withdraw"],
                callback_data="participant:withdraw"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_register"],
                callback_data="participant:register"
            ),
        ],
    ])
