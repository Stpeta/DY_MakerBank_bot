# services/google_sheets.py

import re
from datetime import datetime

import gspread
from gspread.utils import rowcol_to_a1
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import select

from config_data import config
from database.base import AsyncSessionLocal
from database.models import Course, Participant, Transaction

# Авторизация
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
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
    Вписывает коды регистраций в колонку C для каждого email.
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get("Email", "").strip()
        if email in codes:
            sheet.update_cell(idx, 3, codes[email])

def mark_registered(sheet_url: str, email: str) -> None:
    """
    Отмечает столбец D ("Registered") как TRUE для данного email.
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("Email", "").strip().lower() == email.lower():
            sheet.update_cell(idx, 4, "TRUE")
            break


async def update_participant_finances(participant_id: int) -> None:
    """Обновляет данные баланса участника в Google Sheet."""
    async with AsyncSessionLocal() as session:
        participant = await session.get(Participant, participant_id)
        if not participant:
            return

        course = await session.get(Course, participant.course_id)
        if not course or not course.sheet_url:
            return

        ss_id = _normalize_url(course.sheet_url)
        sheet = _gs_client.open_by_key(ss_id).sheet1

        records = sheet.get_all_records()
        row_idx = None
        for idx, row in enumerate(records, start=2):
            if row.get("Email", "").strip().lower() == participant.email.lower():
                row_idx = idx
                break
        if row_idx is None:
            return

        total = participant.balance + participant.savings_balance - participant.loan_balance
        sheet.update_cell(row_idx, 5, float(total))
        sheet.update_cell(row_idx, 6, float(participant.balance))
        sheet.update_cell(row_idx, 7, float(participant.savings_balance))
        sheet.update_cell(row_idx, 8, float(participant.loan_balance))

        # Clear previous operations
        if sheet.col_count >= 9:
            start_a1 = rowcol_to_a1(row_idx, 9)
            end_a1 = rowcol_to_a1(row_idx, sheet.col_count)
            sheet.batch_clear([f"{start_a1}:{end_a1}"])

        # Fetch cash operations
        result = await session.execute(
            select(Transaction)
            .where(Transaction.participant_id == participant_id)
            .where(Transaction.type.in_(["cash_deposit", "cash_withdrawal"]))
            .where(Transaction.status == "completed")
            .order_by(Transaction.created_at)
        )
        operations = result.scalars().all()

        col = 9
        for tx in operations:
            date_str = tx.created_at.strftime("%d.%m")
            if tx.type == "cash_withdrawal":
                text = f"{date_str} -{tx.amount}"
                color = {"red": 1, "green": 0, "blue": 0}
            else:
                text = f"{date_str} {tx.amount}"
                color = {"red": 0, "green": 1, "blue": 0}
            sheet.update_cell(row_idx, col, text)
            sheet.format(rowcol_to_a1(row_idx, col), {"textFormat": {"foregroundColor": color}})
            col += 1

