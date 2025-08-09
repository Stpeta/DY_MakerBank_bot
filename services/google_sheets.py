# services/google_sheets.py

import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config_data import config

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

