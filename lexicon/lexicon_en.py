LEXICON = {
    # region --- Main Menu ---

    "cmd_start": "Start bot",
    "cmd_register": "Register",
    "cmd_about": "About bot",
    "about_text": "MakerBank bot v1.0 by Dmitry Yakovlev\nContact the author: @nedanaec",  # Bot info text

    # endregion --- Main Menu ---

    # region --- Course Management ---

    # Prompts for creating a new course
    "course_name_request": "Enter the name of the new course:",  # Ask admin for course title
    "course_description_request": "Enter the description of the course:",  # Ask admin for course description
    "course_savings_rate_request": "Enter weekly savings interest rate (%)",
    "course_loan_rate_request": "Enter weekly loan interest rate (%)",
    "course_rate_invalid": "Please enter a valid percentage.",
    "course_max_loan_request": "Enter maximum loan amount:",
    "course_savings_lock_request": "Enter savings lock period (days):",
    "course_interest_day_request": "Enter interest payout weekday (0=Monday ... 6=Sunday):",
    "course_interest_time_request": "Enter interest payout time (HH:MM, UTC):",
    "course_value_invalid": "Please enter a valid number.",
    "course_sheet_request": "Please send the Google Sheets link containing the list of participants:",
    # Ask for sheet URL

    # Errors related to Google Sheets
    "course_sheet_invalid": "❌ Failed to read data from Google Sheets. Please check the link and try again.",
    "course_sheet_invalid_format": "❗️ It seems this is not a Google Sheets link. Please send a valid link.",
    "course_sheet_unreachable": "❌ Could not access the sheet. Make sure you have granted access to the service "
                                "account.",
    "course_sheet_empty": "⚠️ The sheet is empty or doesn't contain the columns 'Name' and 'Email'. Please check its "
                          "contents.",

    # Confirmation once a course is created
    "course_created": "✅ Course “{name}” created, {count} participants added. Registration codes have been written to "
                      "the Google Sheets.",

    # Finish Course Flow
    "finish_no_active": "You have no active courses to finish.",
    "finish_select": "Select the course you want to finish:",
    "finish_success": "✅ Course “{name}” has been successfully finished.",

    # endregion --- Course Management ---

    # region --- Participant Registration ---

    # "participant_greeting": "Welcome! Available commands: /balance, /deposit, /withdraw",  # Initial greeting
    "registration_code_request": "Enter your registration code:",  # Ask for code
    # "registration_welcome": 'To join a course, enter your registration code:',  # /start flow
    "registration_not_found": "❌ Code not found. Please check and try again.",  # Invalid code
    "registration_already": "⚠️ You are already registered, {name}.",  # Already registered
    "registration_success": "✅ You have been registered as {name}! Welcome.\n\n"
                            "Now you can use /start to access your banking menu.",  # Success

    "operation_in_progress": "⚠️ Please finish the current operation before starting another one.",

    # endregion --- Participant Registration ---

    # region --- Admin Panel ---

    # Main menu messages
    "admin_main_no_courses": (
        "You have no courses.\n"
        "To create a new one, click “➕ New Course”."
    ),
    "admin_main_has_courses": (
        "You have {active} active and {finished} finished courses.\n"
        "Select one to manage:"
    ),
    # Inline keyboard buttons for admin actions
    "button_new_course": "➕ New Course",  # Start new course creation
    "button_info": "ℹ️ About Bot",  # Show bot info
    "button_finish_course": "🛑 Finish Course",  # End a course
    "button_back": "↩️ Back",  # Navigate back
    "button_edit_name": "✏️ Title",
    "button_edit_description": "✏️ Description",
    "button_edit_interest_day": "📅 Interest day",
    "button_edit_interest_time": "⏰ Interest time",
    "button_edit_savings_rate": "💹 Savings rate",
    "button_edit_loan_rate": "💸 Loan rate",
    "button_edit_max_loan": "⬆️ Max loan",
    "button_edit_savings_lock": "⏳ Savings lock",

    # Emojis indicating course status
    "emoji_active": "🟢",  # Active course
    "emoji_finished": "🛑",  # Finished course

    # Template for displaying course details
    "course_info": (
        "📖 Title: {name}\n"
        "📝 Description: {description}\n"
        "🗓 Created: {created_at:%d.%m.%Y}\n"
        "{course_status_emoji} Status: {status}\n\n"
        "💹 Savings rate: {savings_rate}%\n"
        "💸 Loan rate: {loan_rate}%\n"
        "⬆️ Max loan: {max_loan}\n"
        "⏳ Savings lock: {savings_delay} days\n"
        "📆 Interest payout: {interest_day} {interest_time} UTC\n\n"
        "👥 Total participants: {total}\n"
        "📝 Registered: {registered}\n"
        "💳 Average balance: {avg_balance:.2f}"
    ),

    # Status Values
    "status_active": "active",  # Course is ongoing
    "status_finished": "finished",  # Course has ended

    # endregion --- Admin Panel ---

    # region --- Participant Panel ---

    # Participant Main Menu and Display
    "choose_course_prompt": "Please choose your course:",

    "main_balance_text": (
        "🏫 Course: {course_name}\n"
        "👤 {name}\n\n"
        "💳 Balance: {balance}\n"
        "💹 Savings: {savings} (rate: {savings_rate}%)\n"
        "💸 Loans: {loan} (rate: {loan_rate}%)\n"
    ),  # Overview of participant balances

    # Inline Keyboard Buttons
    "button_withdraw_cash": "💳➔💰 Withdraw Cash",
    "button_deposit_cash": "💰➔💳 Deposit Cash",
    "button_to_savings": "💳➔💹 To Savings",
    "button_from_savings": "💹➔💳 From Savings",
    "button_repay_loan": "💳➔💸 Repay Loan",
    "button_take_loan": "💸➔💳 Take Loan",
    "button_cancel": "❌ Cancel",

    # endregion --- Participant Panel ---

    # region --- Withdraw and Deposit Flows ---

    "withdraw_amount_request": "Enter the amount to withdraw 🪙:",
    "deposit_amount_request": "Enter the amount to deposit 🪙:",

    "invalid_amount": "Please enter a valid positive number.",
    "insufficient_funds": "⚠️ You have insufficient funds.\nEnter the amount to withdraw 🪙:",
    "loan_repay_exceeds_loan_balance": "⚠️ Repay amount cannot exceed the remaining loan balance.",

    # Savings and loans operations
    "to_savings_amount_request": "Enter amount to transfer to savings 🪙:",
    "from_savings_amount_request": "Enter amount to withdraw from savings 🪙:",
    "take_loan_amount_request": "Enter loan amount 🪙:",
    "repay_loan_amount_request": "Enter amount to repay 🪙:",
    "savings_deposit_success": "✅ {amount} 🪙 moved to savings.",
    "savings_withdraw_success": "✅ {amount} 🪙 withdrawn from savings.",
    "loan_take_success": "✅ Loan of {amount} 🪙 issued.",
    "loan_repay_success": "✅ Loan repaid by {amount} 🪙.",
    "savings_locked_until": "⚠️ Savings are locked until {unlock_time:%d.%m.%Y %H:%M UTC}.",
    "savings_lock_warning": "\n<i>⚠️️ After deposit, funds cannot be withdrawn for {days} days (until {unlock_time:%d.%m.%Y %H:%M UTC}).</i>",
    "savings_insufficient": "⚠️ You don't have that much in savings.",
    "loan_limit_reached": "⚠️ Loan limit is {limit} 🪙.",

    "withdraw_waiting_approval": "Your withdrawal request of {amount} 🪙 is pending operator approval.\n"
                                 "<code>{course_name}, {name}, tx_id: {tx_id}</code>",
    "deposit_waiting_approval": "Your deposit request of {amount} 🪙 is pending operator approval.\n"
                                "<code>{course_name}, {name}, tx_id: {tx_id}</code>",

    "cash_request_cancelled": "Your request has been cancelled.\n<code>{course_name}, {name}, tx_id: {tx_id}</code>",

    # Buttons for admin to approve/decline
    "button_approve": "✅ Approve",
    "button_decline": "❌ Decline",

    # Admin notifications when user creates a request
    "admin_withdraw_request": "<b>🏫 {course_name}</b>\n💳➔💰\n👤 {name} requests withdrawal of {amount} 🪙\n(tx_id: {tx_id})",
    "admin_deposit_request": "<b>🏫 {course_name}</b>\n💰➔💳\n👤 {name} requests deposit of {amount} 🪙\n(tx_id: {tx_id})",

    # Admin UI messages after handling
    "admin_tx_approved_admin": "✅ Transaction approved.\n<code>{course_name}, {name}, tx_id: {tx_id}</code>",
    "admin_tx_declined_admin": "❌ Transaction declined.\n<code>{course_name}, {name}, tx_id: {tx_id}</code>",
    "admin_tx_cancelled_admin": "🚫 Transaction canceled by participant.\n<code>{course_name}, {name}, tx_id: {tx_id}</code>",

    # Participant notifications on approval/decline
    "withdraw_approved": "✅ Your withdrawal of {amount} 🪙 has been approved.\n"
                         "<code>{course_name}, {name}, tx_id: {tx_id}</code>",
    "withdraw_declined": "❌ Your withdrawal request of {amount} 🪙 has been declined.\n"
                         "<code>{course_name}, {name}, tx_id: {tx_id}</code>",
    "deposit_approved": "✅ Your deposit of {amount} 🪙 has been approved and added to your balance.\n"
                        "<code>{course_name}, {name}, tx_id: {tx_id}</code>",
    "deposit_declined": "❌ Your deposit request of {amount} 🪙 has been declined.\n"
                        "<code>{course_name}, {name}, tx_id: {tx_id}</code>",

    # Interest accrual notifications
    "interest_savings": "{course_name}\n💹 {amount} 🪙 interest added to your savings.",
    "interest_loan": "{course_name}\n💸️ {amount} 🪙 interest added to your loan in.",
    "interest_admin_stats": (
        "Weekly interest applied for {course_name}:\n"
        "💹 Savings: {s_count} participants, total {s_total} 🪙\n"
        "💸️ Loan: {l_count} participants, total {l_total} 🪙"
    ),

    # region --- Withdraw and Deposit Flows ---

}
