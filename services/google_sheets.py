# services/google_sheets.py

import logging
import re
from decimal import Decimal

import gspread
from gspread_formatting import (
    CellFormat,
    Color,
    DataValidationRule,
    BooleanCondition,
    format_cell_ranges,
    set_column_width,
    set_data_validation_for_cell_range,
)
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import config
from database.base import AsyncSessionLocal
from database.models import Course, Participant
from lexicon.lexicon_en import LEXICON

# Authorization
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_creds = ServiceAccountCredentials.from_json_keyfile_name(
    config.SERVICE_ACCOUNT_FILE, SCOPES
)
_gs_client = gspread.authorize(_creds)
logger = logging.getLogger(__name__)

# Regex for validating the sheet URL
_SHEET_URL_RE = re.compile(r"^https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)")

def is_valid_sheet_url(url: str) -> bool:
    return bool(_SHEET_URL_RE.match(url))

def _normalize_url(url: str) -> str:
    m = _SHEET_URL_RE.match(url)
    return m.group(1) if m else url

def fetch_students(sheet_url: str) -> list[dict[str, str]]:
    """Read first worksheet and return rows as dictionaries."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    return sheet.get_all_records()

def write_registration_codes(sheet_url: str, codes: dict[str, str]) -> None:
    """Write registration codes to column F for each email."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get(LEXICON["sheet_header_email"], "").strip()
        if email in codes:
            sheet.update_cell(idx, 6, codes[email])

def mark_registered(sheet_url: str, email: str) -> None:
    """Mark column G ("Registered") as TRUE for the given email."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get(LEXICON["sheet_header_email"], "").strip().lower() == email.lower():
            sheet.update_cell(idx, 7, "TRUE")
            break


def write_telegram_data(sheet_url: str, data: dict[str, tuple[int | None, str | None]]) -> None:
    """Write Telegram ID and username into columns D and E.

    Args:
        sheet_url: URL of the target spreadsheet.
        data: Mapping of email to ``(telegram_id, telegram_username)``.
    """
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get(LEXICON["sheet_header_email"], "").strip().lower()
        if email in data:
            tg_id, username = data[email]
            if tg_id is not None:
                sheet.update_cell(idx, 4, str(tg_id))
            if username:
                sheet.update_cell(idx, 5, username)


def prepare_course_sheet(sheet_url: str) -> None:
    """Prepare a new spreadsheet for course usage."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    sheet.clear()
    sheet.freeze(rows=1)
    headers = [
        LEXICON["sheet_header_name"],
        LEXICON["sheet_header_email"],
        LEXICON["sheet_header_comment"],
        LEXICON["sheet_header_tg_id"],
        LEXICON["sheet_header_tg_nick"],
        LEXICON["sheet_header_reg_code"],
        LEXICON["sheet_header_registered"],
        LEXICON["sheet_header_total"],
        LEXICON["sheet_header_wallet"],
        LEXICON["sheet_header_savings"],
        LEXICON["sheet_header_loan"],
    ]
    sheet.update("A1:K1", [headers])
    set_column_width(sheet, "G:G", 70)
    rule = DataValidationRule(BooleanCondition("BOOLEAN"), showCustomUi=True)
    set_data_validation_for_cell_range(sheet, "G2:G", rule)
    sheet.add_protected_range(
        name="D:K",
        description=LEXICON["sheet_protected_warning"],
        warning_only=True,
    )
    format_cell_ranges(
        sheet,
        [("D:K", CellFormat(backgroundColor=Color(1, 0.9, 0.9)))],
    )


async def _collect_balance_data(
    session: AsyncSession, course_id: int
) -> tuple[str, dict[str, tuple[float, float, float, float]]]:
    """Collect wallet, savings and loan data for all course participants."""
    course = await session.get(Course, course_id)
    result = await session.execute(
        select(Participant).where(Participant.course_id == course_id)
    )
    participants = result.scalars().all()

    data: dict[str, tuple[float, float, float, float]] = {}
    for p in participants:
        wallet = Decimal(p.wallet_balance) if p.wallet_balance is not None else Decimal("0")
        savings = Decimal(p.savings_balance) if p.savings_balance is not None else Decimal("0")
        loan = Decimal(p.loan_balance) if p.loan_balance is not None else Decimal("0")
        total_balance = wallet + savings - loan
        data[p.email.strip().lower()] = (
            float(total_balance), float(wallet), float(savings), float(loan)
        )

    return course.sheet_url, data


def _write_balances_to_sheet(
    sheet_url: str, data: dict[str, tuple[float, float, float, float]]
) -> None:
    """Write wallet, savings and loan balances into the course Google Sheet."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    # Header row
    sheet.update(
        "H1:K1",
        [[
            LEXICON["sheet_header_total"],
            LEXICON["sheet_header_wallet"],
            LEXICON["sheet_header_savings"],
            LEXICON["sheet_header_loan"],
        ]],
    )
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get(LEXICON["sheet_header_email"], "").strip().lower()
        if email in data:
            sheet.update(f"H{idx}:K{idx}", [list(data[email])])


async def update_course_balances(course_id: int) -> None:
    """Update a course's Google Sheet with participant wallet/savings/loan balances."""
    async with AsyncSessionLocal() as session:
        sheet_url, data = await _collect_balance_data(session, course_id)

    if sheet_url:
        _write_balances_to_sheet(sheet_url, data)

