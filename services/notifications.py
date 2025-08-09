# services/notifications.py

from typing import Optional, Any

from aiogram import Bot

from database.base import AsyncSessionLocal
from database.models import Participant, Course


async def send_message_to_telegram_id(
        bot: Bot,
        chat_id: int,
        text: str,
        reply_markup: Optional[Any] = None
) -> None:
    """
    Send a message to any Telegram chat by its chat_id.
    """
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup
    )


async def send_message_to_participant(
        bot: Bot,
        participant_id: int,
        text: str,
        reply_markup: Optional[Any] = None
) -> None:
    """
    Lookup a participant by database ID and send them a message.
    Assumes Participant.telegram_id stores the correct telegram_id.
    """
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        if participant and participant.telegram_id:
            await send_message_to_telegram_id(
                bot,
                participant.telegram_id,
                text,
                reply_markup=reply_markup
            )


async def send_message_to_course_creator(
        bot: Bot,
        course_id: int,
        text: str,
        reply_markup: Optional[Any] = None
) -> None:
    """
    Lookup a course by database ID, find its creator_id (admin's chat_id),
    and send them a message.
    """
    async with AsyncSessionLocal() as session:
        course = await session.get(Course, course_id)
        if course and course.creator_id:
            await send_message_to_telegram_id(
                bot,
                course.creator_id,
                text,
                reply_markup=reply_markup
            )
