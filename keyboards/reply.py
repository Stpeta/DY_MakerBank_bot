from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/balance"), KeyboardButton(text="/deposit")],
            [KeyboardButton(text="/withdraw"), KeyboardButton(text="/register")]
        ],
        resize_keyboard=True
    )