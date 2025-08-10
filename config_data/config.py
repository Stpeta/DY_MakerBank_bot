from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

@dataclass
class DB:
    url: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DB
    SERVICE_ACCOUNT_FILE: str
    POSTMARK_API_TOKEN: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        ),
        db=DB(
            url="sqlite+aiosqlite:////db/makerbank.db"
        ),
        SERVICE_ACCOUNT_FILE="service_account.json",
        POSTMARK_API_TOKEN = env('POSTMARK_API_TOKEN')
    )
