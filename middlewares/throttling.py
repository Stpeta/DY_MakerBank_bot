import time
from aiogram import BaseMiddleware
from aiogram.types import Message, Update


class ThrottlingMiddleware(BaseMiddleware):
    """
    Простое ограничение частоты сообщений (antiflood).
    Блокирует повторные запросы от одного пользователя чаще, чем раз в `limit` секунд.
    """

    def __init__(self, limit: float = 1.0):
        self.limit = limit
        # Храним последнее время обращения в UNIX timestamp
        self.user_timestamps: dict[int, float] = {}
        super().__init__()

    async def __call__(self, handler, event: Update, data):
        # Пытаемся получить объект Message из Update
        message: Message | None = None
        if hasattr(event, 'message'):
            message = event.message
        elif hasattr(event, 'edited_message'):
            message = event.edited_message
        # Если нет сообщения, просто пропускаем
        if message is None:
            return await handler(event, data)

        user_id = message.from_user.id
        now = time.time()
        last_time = self.user_timestamps.get(user_id, 0)
        # Если пришло слишком быстро, блокируем и не вызываем хендлер
        if now - last_time < self.limit:
            return
        # Иначе обновляем отметку и передаем выполнение
        self.user_timestamps[user_id] = now
        return await handler(event, data)
