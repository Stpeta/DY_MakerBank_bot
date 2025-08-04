from aiogram.types import BotCommand
from lexicon.lexicon_en import LEXICON

# Описания команд
COMMON_COMMANDS = {
    "start": LEXICON["cmd_start"],
    "about": LEXICON["cmd_about"],
}

def get_main_menu_commands() -> list[BotCommand]:
    """
    Возвращает список BotCommand для основного меню (общие команды).
    """
    return [
        BotCommand(command=f"/{cmd}", description=desc)
        for cmd, desc in COMMON_COMMANDS.items()
    ]
