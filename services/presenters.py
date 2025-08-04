from lexicon.lexicon_en import LEXICON

def render_course_info(course, stats: dict) -> str:
    """
    Собирает текст карточки курса.
    Подставляет:
      - course.created_at  (дата создания)
      - course_status_emoji (в зависимости от course.is_active)
      - status             (текст статуса из лексикона)
      - остальное из stats
    """
    # Выбираем эмодзи
    course_status_emoji = (
        LEXICON["emoji_active"]
        if course.is_active
        else LEXICON["emoji_finished"]
    )
    # Текст статуса
    status = (
        LEXICON["status_active"]
        if course.is_active
        else LEXICON["status_finished"]
    )
    # Собираем
    return LEXICON["course_info"].format(
        name                = course.name,
        description         = course.description,
        created_at          = course.created_at,
        course_status_emoji = course_status_emoji,
        status              = status,
        total               = stats["total"],
        registered          = stats["registered"],
        avg_balance         = stats["avg_balance"],
    )
