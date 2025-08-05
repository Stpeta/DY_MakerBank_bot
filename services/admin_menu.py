#services/admin_menu.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.base import AsyncSessionLocal
from database.crud import get_all_courses_by_admin
from lexicon.lexicon_en import LEXICON
from keyboards.admin import main_menu_admin_kb

async def build_admin_menu(user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    async with AsyncSessionLocal() as session:
        all_courses = await get_all_courses_by_admin(session, user_id)

    if not all_courses:
        text = LEXICON["admin_main_no_courses"]
        kb   = main_menu_admin_kb()
        return text, kb

    active   = sorted([c for c in all_courses if c.is_active],
                      key=lambda c: c.name.lower())
    finished = sorted([c for c in all_courses if not c.is_active],
                      key=lambda c: c.name.lower())

    text = LEXICON["admin_main_has_courses"].format(
        active=len(active), finished=len(finished)
    )

    rows = [
        [InlineKeyboardButton(
            text=f"{LEXICON['emoji_active']} {c.name}",
            callback_data=f"admin:course:info:{c.id}"
        )] for c in active
    ] + [
        [InlineKeyboardButton(
            text=f"{LEXICON['emoji_finished']} {c.name}",
            callback_data=f"admin:course:info:{c.id}"
        )] for c in finished
    ]
    rows += main_menu_admin_kb().inline_keyboard
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return text, kb
