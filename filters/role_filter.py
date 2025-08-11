from aiogram.filters import BaseFilter
from aiogram.types import Message
from services.role_service import get_user_role

class RoleFilter(BaseFilter):
    """Filter that allows events only for users with the specified role."""

    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message) -> bool:
        """Check whether the sender's role matches the expected one."""
        actual = await get_user_role(message.from_user.id)
        return actual == self.role
