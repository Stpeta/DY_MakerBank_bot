from aiogram.types import BotCommand
from lexicon.lexicon_en import LEXICON

# Descriptions for common bot commands
COMMON_COMMANDS = {
    "start": LEXICON["cmd_start"],
    # "register": LEXICON["cmd_register"],
    # "about": LEXICON["cmd_about"],
}

def get_main_menu_commands() -> list[BotCommand]:
    """Return a list of ``BotCommand`` for the main menu."""
    return [
        BotCommand(command=f"/{cmd}", description=desc)
        for cmd, desc in COMMON_COMMANDS.items()
    ]
