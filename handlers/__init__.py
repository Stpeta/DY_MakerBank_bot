"""Message handlers registration."""
from aiogram import Dispatcher

from .admin import admin_router
from .common import common_router
from .participant import participant_router
from .registration import registration_router


def register_handlers(dp: Dispatcher) -> None:
    """Include all routers into the dispatcher."""
    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(participant_router)
    dp.include_router(registration_router)
