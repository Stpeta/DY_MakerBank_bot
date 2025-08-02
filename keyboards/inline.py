from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def example_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍", callback_data="like")],
        [InlineKeyboardButton(text="👎", callback_data="dislike")]
    ])