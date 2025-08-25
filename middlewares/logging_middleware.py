import logging
from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user messages and identifiers."""

    async def __call__(self, handler, event: Update, data: dict):
        """Process an update and log message text with user id.

        Args:
            handler: Next middleware or handler in the chain.
            event: Incoming update instance.
            data: Contextual data for the handler.

        Returns:
            Any: Result returned by the next handler.
        """
        message = None
        user_id = None
        text = None

        if getattr(event, "message", None):
            message = event.message
        elif getattr(event, "edited_message", None):
            message = event.edited_message
        elif getattr(event, "callback_query", None):
            callback = event.callback_query
            message = callback.message
            text = callback.data
            user_id = callback.from_user.id

        if message is not None:
            if text is None:
                text = message.text or message.caption or ""
            if user_id is None and getattr(message, "from_user", None):
                user_id = message.from_user.id

        if text is not None and user_id is not None:
            logger.info("Update from %s: %s", user_id, text)

        return await handler(event, data)
