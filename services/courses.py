import csv, random, string
from io import StringIO
from database.crud import (
    create_course, add_participants,
    get_participant_by_code, register_participant
)
from database.base import AsyncSessionLocal

def _gen_code(existing: set[str]) -> str:
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in existing:
            return code

async def create_new_course(name: str, description: str, creator_id: int, csv_bytes: bytes):
    text = csv_bytes.decode('utf-8-sig')
    reader = csv.DictReader(StringIO(text))
    participants = []
    existing = set()
    for row in reader:
        code = _gen_code(existing)
        existing.add(code)
        participants.append({
            "name": row["Name"],
            "email": row["Email"],
            "registration_code": code
        })
    async with AsyncSessionLocal() as session:
        course = await create_course(session, name, description, creator_id)
        await add_participants(session, course.id, participants)
    return course, participants

async def register_by_code(code: str, telegram_id: int):
    async with AsyncSessionLocal() as session:
        part = await get_participant_by_code(session, code)
        if not part:
            return None, "not_found"
        if part.is_registered:
            return part, "already"
        part = await register_participant(session, part, telegram_id)
        return part, "ok"