from aiogram.filters import BaseFilter
from aiogram.types import Message
from services.role_service import get_user_role

class RoleFilter(BaseFilter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message) -> bool:
        actual = await get_user_role(message.from_user.id)
        return actual == self.role
