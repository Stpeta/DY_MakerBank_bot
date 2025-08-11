# services/admin_menu.py

from aiogram.types import InlineKeyboardMarkup

from database.base import AsyncSessionLocal
from database.crud_courses import get_all_courses_by_admin
from keyboards.admin import admin_menu_kb
from services.presenters import render_admin_menu


async def build_admin_menu(user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """Builds text and keyboard for the admin main menu."""
    async with AsyncSessionLocal() as session:
        courses = await get_all_courses_by_admin(session, user_id)

    active = sorted((c for c in courses if c.is_active), key=lambda c: c.name.lower())
    finished = sorted((c for c in courses if not c.is_active), key=lambda c: c.name.lower())

    text = render_admin_menu(len(active), len(finished))
    kb = admin_menu_kb(active + finished)
    return text, kb
