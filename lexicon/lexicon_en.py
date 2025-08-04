LEXICON = {
    # Запрос названия курса
    "course_name_request": "Введите название нового курса:",
    # Запрос описания курса
    "course_description_request": "Введите описание курса:",
    # Запрос ссылки на Google Sheet
    "course_sheet_request": "Пришлите ссылку на Google Sheet со списком участников:",
    # Ошибка при чтении таблицы
    "course_sheet_invalid": "❌ Не удалось прочитать данные из Google Sheets. Проверьте ссылку и попробуйте снова.",
    # Подтверждение создания курса
    "course_created": "✅ Курс «{name}» создан, добавлено {count} участников. Коды регистрации внесены в Google Sheets.",

    "course_sheet_invalid_format":
        "❗️ Похоже, это не ссылка на Google Sheets. Проверьте и пришлите корректную ссылку.",
    "course_sheet_unreachable":
        "❌ Не удалось получить доступ к таблице. Убедитесь, что вы дали доступ сервисному аккаунту.",
    "course_sheet_empty":
        "⚠️ Таблица пуста или не содержит колонок Name и Email. Проверьте содержимое.",

    # Старые ключи, их трогать не нужно
    "participant_greeting": "Добро пожаловать! Доступные команды: /balance, /deposit, /withdraw",
    "registration_code_request": "Введите ваш registration code:",
    "registration_success": "Вы успешно зарегистрированы, {name}!",
    "registration_already": "Вы уже зарегистрированы, {name}. Если ошибка — обратитесь к администратору.",
    "registration_not_found": "Код не найден. Проверьте и попробуйте снова.",

    # При /start — приглашение ввести код для регистрации
    "registration_welcome": 'Чтобы присоединиться к курсу "{course_name}", введите ваш registration code:',
    # Код не найден
    "registration_not_found": "❌ Код не найден. Проверьте и попробуйте снова.",
    # Уже зарегистрирован
    "registration_already": "⚠️ Вы уже зарегистрированы, {name}.",
    # Успешная регистрация
    "registration_success": "✅ Вы зарегистрированы как {name}! Добро пожаловать.",


    # Завершение курса
    "finish_no_active": "У вас нет активных курсов для завершения.",
    "finish_select": "Выберите курс, который хотите завершить:",
    "finish_success": "✅ Курс «{name}» успешно завершён.",

    # Админка
    "admin_main_no_courses": (
        "У вас нет ни одного курса.\n"
        "Чтобы создать новый — нажмите «➕ Новый курс»."
    ),
    "admin_main_has_courses": (
        "У вас {active} активных и {finished} завершённых курсов.\n"
        "Выберите курс для работы:"
    ),
    # Кнопка «О боте»
    "admin_info": "MakerBank bot v.1.0 by Dmitry Yakovlev\nContact the author: @nedanaec",

    # Кнопки в inline-клавиатуре админа
    "button_new_course":    "➕ Новый курс",
    "button_info":          "ℹ️ О боте",
    "button_finish_course": "🛑 Завершить курс",
    "button_back":          "↩️ Назад",
    # Эмоджи для курсов
    "emoji_active":   "🟢",
    "emoji_finished": "🛑",

    "course_info": (
        "📖 Название: {name}\n"
        "📝 Описание: {description}\n"
        "🗓 Создан: {created_at:%d.%m.%Y}\n"
        "{course_status_emoji} Статус: {status}\n\n"
        "👥 Всего участников: {total}\n"
        "📝 Зарегистрировано: {registered}\n"
        "💰 Средний баланс: {avg_balance:.2f}"
    ),

    # Значения статуса
    "status_active": "активен",
    "status_finished": "завершён",

    # Кнопки в inline-клавиатуре участника
    "button_balance": "Баланс",
    "button_deposit": "Пополнить",
    "button_withdraw": "Вывести",
    "button_register": "Регистрация",

    # Команды бота
    "cmd_start": "Запустить бота",
    "cmd_about": "О боте",
    "about_text": "MakerBank bot v.1.0 by Dmitry Yakovlev\nContact the author: @nedanaec"
}
