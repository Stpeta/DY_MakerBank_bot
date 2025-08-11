from calendar import day_name
from lexicon.lexicon_en import LEXICON


def render_course_info(course, stats: dict, savings_rate: float, loan_rate: float) -> str:
    """Build formatted course information text for display."""
    # Choose emoji based on course activity
    course_status_emoji = (
        LEXICON["emoji_active"]
        if course.is_active
        else LEXICON["emoji_finished"]
    )
    # Status text
    status = (
        LEXICON["status_active"]
        if course.is_active
        else LEXICON["status_finished"]
    )
    # Compose final message
    return LEXICON["course_info"].format(
        name=course.name,
        description=course.description,
        created_at=course.created_at,
        course_status_emoji=course_status_emoji,
        status=status,
        sheet_url=course.sheet_url or "-",
        total=stats["total"],
        registered=stats["registered"],
        avg_balance=stats["avg_balance"],
        savings_rate=savings_rate,
        loan_rate=loan_rate,
        max_loan=course.max_loan_amount,
        savings_delay=course.savings_withdrawal_delay,
        interest_day=day_name[course.interest_day],
        interest_time=course.interest_time,
    )


def render_participant_info(
    name: str,
    course_name: str,
    balance,
    savings,
    loan,
    savings_rate: float,
    loan_rate: float,
) -> str:
    """Compose a text snippet with the participant's balances."""
    return LEXICON["main_balance_text"].format(
        name=name,
        course_name=course_name,
        balance=balance,
        savings=savings,
        loan=loan,
        savings_rate=savings_rate,
        loan_rate=loan_rate,
    )


def render_admin_menu(active: int, finished: int) -> str:
    """Generate text for the admin main menu based on course counts."""
    if active + finished == 0:
        return LEXICON["admin_main_no_courses"]
    return LEXICON["admin_main_has_courses"].format(active=active, finished=finished)
