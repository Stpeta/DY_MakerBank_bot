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

# Authorization
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_creds = ServiceAccountCredentials.from_json_keyfile_name(
    config.SERVICE_ACCOUNT_FILE, SCOPES
)
_gs_client = gspread.authorize(_creds)

# Regex for validating the sheet URL
_SHEET_URL_RE = re.compile(r"^https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)")

def is_valid_sheet_url(url: str) -> bool:
    return bool(_SHEET_URL_RE.match(url))

def _normalize_url(url: str) -> str:
    m = _SHEET_URL_RE.match(url)
    return m.group(1) if m else url

def fetch_students(sheet_url: str) -> list[tuple[str, str]]:
    """Read first worksheet and return a list of (name, email)."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    rows = sheet.get_all_values()[1:]  # skip header row
    return [(r[0].strip(), r[1].strip()) for r in rows if len(r) >= 2]

def write_registration_codes(
    sheet_url: str,
    codes: dict[str, str]
) -> None:
    """Write registration codes to column C for each email."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get("Email", "").strip()
        if email in codes:
            sheet.update_cell(idx, 3, codes[email])

def mark_registered(sheet_url: str, email: str) -> None:
    """Mark column D ("Registered") as TRUE for the given email."""
    ss_id = _normalize_url(sheet_url)
    sheet = _gs_client.open_by_key(ss_id).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("Email", "").strip().lower() == email.lower():
            sheet.update_cell(idx, 4, "TRUE")
            break


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
    sheet.update("F1:I1", [["Total", "Wallet", "Savings", "Loan"]])
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        email = row.get("Email", "").strip().lower()
        if email in data:
            sheet.update(f"F{idx}:I{idx}", [list(data[email])])


async def update_course_balances(course_id: int) -> None:
    """Update a course's Google Sheet with participant wallet/savings/loan balances."""
    async with AsyncSessionLocal() as session:
        sheet_url, data = await _collect_balance_data(session, course_id)

    if sheet_url:
        _write_balances_to_sheet(sheet_url, data)

