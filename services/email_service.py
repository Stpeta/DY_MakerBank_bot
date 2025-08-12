"""Utilities for sending emails."""

import logging
from postmarker.core import PostmarkClient

from config_data import config
from lexicon.lexicon_en import LEXICON

logger = logging.getLogger(__name__)
_client = PostmarkClient(server_token=config.POSTMARK_API_TOKEN)
_SENDER = "no-reply@dmitryyakovlev.space"


def send_registration_code(recipient: str, code: str, course: str, name: str) -> None:
    """Send a registration code email.

    Args:
        recipient: Email address of the participant.
        code: Registration code to deliver.
        course: Name of the course.
        name: Participant's name.

    Raises:
        Exception: Propagates errors from the Postmark client.
    """
    subject = LEXICON["email_regcode_subject"].format(course=course)
    body = LEXICON["email_regcode_body"].format(name=name, code=code)
    _client.emails.send(
        From=_SENDER,
        To=recipient,
        Subject=subject,
        HtmlBody=f"<p>{body}</p>",
    )
    logger.debug("Email accepted for %s", recipient)
