from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lexicon.lexicon_en import LEXICON

# Participant Main Menu Keyboard
# Shows only banking operation buttons; no cancel button here.
def main_menu_participant_kb() -> InlineKeyboardMarkup:
    """
    Inline keyboard for participant main menu with banking operations.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON["button_withdraw_cash"],
                callback_data="participant:withdraw_cash"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_deposit_cash"],
                callback_data="participant:deposit_cash"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_to_savings"],
                callback_data="participant:to_savings"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_from_savings"],
                callback_data="participant:from_savings"
            ),
        ],
        [
            InlineKeyboardButton(
                text=LEXICON["button_take_loan"],
                callback_data="participant:take_loan"
            ),
            InlineKeyboardButton(
                text=LEXICON["button_repay_loan"],
                callback_data="participant:repay_loan"
            ),
        ],
    ])

# Cancel Operation Keyboard
# Rendered only during an ongoing operation to allow cancellation.
def cancel_operation_kb() -> InlineKeyboardMarkup:
    """
    Inline keyboard with a single Cancel button for aborting operations.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON["button_cancel"],
                callback_data="participant:cancel"
            ),
        ],
    ])
