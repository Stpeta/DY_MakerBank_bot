import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config_data.config import load_config

config = load_config()

# Области доступа
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Авторизация
_creds = ServiceAccountCredentials.from_json_keyfile_name(
    config.SERVICE_ACCOUNT_FILE, SCOPES
)
_gs_client = gspread.authorize(_creds)


def _normalize_url(url: str) -> str:
    """
    Извлекает чистый spreadsheet_id из ссылки.
    """
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else url


def fetch_students(sheet_url: str) -> list[tuple[str,str]]:
    """
    Возвращает список (name, email) из первой вкладки.
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    # Предполагаем, что первая строка — заголовки: Name, Email
    rows = sheet.get_all_values()[1:]
    return [(row[0].strip(), row[1].strip()) for row in rows if len(row) >= 2]


def write_registration_codes(sheet_url: str, codes: dict[str,str]) -> None:
    """
    Вписывает registration_code для каждого email во второй столбец (или в колонку C).
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    all_data = sheet.get_all_records()
    # Пробегаемся по имеющимся строкам и обновляем код
    for idx, row in enumerate(all_data, start=2):  # start=2 т.к. первая строка — заголовки
        email = row.get("Email") or row.get("email")
        if email in codes:
            sheet.update_cell(idx, 3, codes[email])  # записать в колонку C
