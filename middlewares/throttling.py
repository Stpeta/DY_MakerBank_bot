import time
from aiogram import BaseMiddleware
from aiogram.types import Message, Update


class ThrottlingMiddleware(BaseMiddleware):
    """Simple message rate limiter to prevent spam."""

    def __init__(self, limit: float = 1.0):
        self.limit = limit
        # Store last request time per user in UNIX timestamp
        self.user_timestamps: dict[int, float] = {}
        super().__init__()

    async def __call__(self, handler, event: Update, data):
        # Try to get Message object from Update
        message: Message | None = None
        if hasattr(event, 'message'):
            message = event.message
        elif hasattr(event, 'edited_message'):
            message = event.edited_message
        # If no message, pass through
        if message is None:
            return await handler(event, data)

        user_id = message.from_user.id
        now = time.time()
        last_time = self.user_timestamps.get(user_id, 0)
        # Block if requests come faster than limit
        if now - last_time < self.limit:
            return
        # Otherwise update timestamp and continue
        self.user_timestamps[user_id] = now
        return await handler(event, data)
