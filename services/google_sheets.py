# services/google_sheets.py

import re
from decimal import Decimal
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import config
from database.base import AsyncSessionLocal
from database.models import Course, Participant
from lexicon.lexicon_en import LEXICON

# Авторизация
# Добавляем Drive scope, чтобы иметь возможность создавать и шарить таблицы
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
_creds = ServiceAccountCredentials.from_json_keyfile_name(
    config.SERVICE_ACCOUNT_FILE, SCOPES
)
_gs_client = gspread.authorize(_creds)

# Регэксп для проверки URL
_SHEET_URL_RE = re.compile(r"^https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)")

def is_valid_sheet_url(url: str) -> bool:
    return bool(_SHEET_URL_RE.match(url))

def _normalize_url(url: str) -> str:
    m = _SHEET_URL_RE.match(url)
    return m.group(1) if m else url


def create_course_sheet(course_name: str, admin_email: str) -> str:
    """Создаёт новую таблицу курса, настраивает её и выдаёт права админу."""
    title = f"{course_name} MakerBank"
    ss = _gs_client.create(title)
    ss.share(admin_email, perm_type="user", role="writer")
    sheet = ss.sheet1

    headers = [
        LEXICON["sheet_col_name"],
        LEXICON["sheet_col_email"],
        LEXICON["sheet_col_comment"],
        LEXICON["sheet_col_regcode"],
        LEXICON["sheet_col_registered"],
        LEXICON["sheet_col_total"],
        LEXICON["sheet_col_wallet"],
        LEXICON["sheet_col_savings"],
        LEXICON["sheet_col_loan"],
    ]
    sheet.update("A1:I1", [headers])

    # колонка E (Registered) как чекбоксы
    ss.batch_update({
        "requests": [{
            "setDataValidation": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "startColumnIndex": 4,
                    "endColumnIndex": 5,
                },
                "rule": {
                    "condition": {"type": "BOOLEAN"},
                    "strict": True,
                    "showCustomUi": True,
                },
            }
        }]
    })

    # защита колонок D:I
    ss.batch_update({
        "requests": [{
            "addProtectedRange": {
                "protectedRange": {
                    "range": {
                        "sheetId": sheet.id,
                        "startColumnIndex": 3,
                        "endColumnIndex": 9,
                    },
                    "description": "Не редактируйте это если только абсолютно не уверены в том, что делаете",
                    "warningOnly": True,
                }
            }
        }]
    })

    return ss.url

def fetch_students(sheet_url: str) -> list[tuple[str, str]]:
    """
    Читает первый лист, возвр. список (name, email).
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    rows = sheet.get_all_values()[1:]  # пропускаем заголовок
    return [(r[0].strip(), r[1].strip()) for r in rows if len(r) >= 2]

def write_registration_codes(
    sheet_url: str,
    codes: dict[str, str]
) -> None:
    """
    Вписывает коды регистраций в колонку D для каждого email.
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get("Email", "").strip()
        if email in codes:
            sheet.update_cell(idx, 4, codes[email])

def mark_registered(sheet_url: str, email: str) -> None:
    """
    Отмечает столбец E ("Registered") как TRUE для данного email.
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("Email", "").strip().lower() == email.lower():
            sheet.update_cell(idx, 5, "TRUE")
            break


async def _collect_balance_data(
    session: AsyncSession, course_id: int
) -> tuple[str, dict[str, tuple[float, float, float, float]]]:
    """Собирает данные о балансах участников курса."""
    course = await session.get(Course, course_id)
    result = await session.execute(
        select(Participant).where(Participant.course_id == course_id)
    )
    participants = result.scalars().all()

    data: dict[str, tuple[float, float, float, float]] = {}
    for p in participants:
        balance = Decimal(p.balance) if p.balance is not None else Decimal("0")
        savings = Decimal(p.savings_balance) if p.savings_balance is not None else Decimal("0")
        loan = Decimal(p.loan_balance) if p.loan_balance is not None else Decimal("0")
        total = balance + savings - loan
        data[p.email.strip().lower()] = (
            float(total), float(balance), float(savings), float(loan)
        )

    return course.sheet_url, data


def _write_balances_to_sheet(
    sheet_url: str, data: dict[str, tuple[float, float, float, float]]
) -> None:
    """Записывает балансы в гугл-таблицу курса."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    # Заголовки
    sheet.update(
        "F1:I1",
        [[
            LEXICON["sheet_col_total"],
            LEXICON["sheet_col_wallet"],
            LEXICON["sheet_col_savings"],
            LEXICON["sheet_col_loan"],
        ]],
    )
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get("Email", "").strip().lower()
        if email in data:
            sheet.update(f"F{idx}:I{idx}", [list(data[email])])


async def update_course_balances(course_id: int) -> None:
    """Обновляет гугл-таблицу курса балансами участников."""
    async with AsyncSessionLocal() as session:
        sheet_url, data = await _collect_balance_data(session, course_id)

    if sheet_url:
        _write_balances_to_sheet(sheet_url, data)

