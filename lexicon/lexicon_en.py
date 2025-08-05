LEXICON = {
    # region --- Main Menu ---

    "cmd_start": "Start bot",
    "cmd_about": "About bot",
    "about_text": "MakerBank bot v1.0 by Dmitry Yakovlev\nContact the author: @nedanaec",  # Bot info text

    # endregion --- Main Menu ---

    # region --- Course Management ---

    # Prompts for creating a new course
    "course_name_request": "Enter the name of the new course:",  # Ask admin for course title
    "course_description_request": "Enter the description of the course:",  # Ask admin for course description
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
    "registration_success": "✅ You have been registered as {name}! Welcome.",  # Success

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

    # Emojis indicating course status
    "emoji_active": "🟢",  # Active course
    "emoji_finished": "🛑",  # Finished course

    # Template for displaying course details
    "course_info": (
        "📖 Title: {name}\n"
        "📝 Description: {description}\n"
        "🗓 Created: {created_at:%d.%m.%Y}\n"
        "{course_status_emoji} Status: {status}\n\n"
        "👥 Total participants: {total}\n"
        "📝 Registered: {registered}\n"
        "💰 Average balance: {avg_balance:.2f}"
    ),

    # Status Values
    "status_active": "active",  # Course is ongoing
    "status_finished": "finished",  # Course has ended

    # endregion --- Admin Panel ---

    # region --- Participant Panel ---

    # Participant Main Menu and Display
    "main_balance_text": (
        "👤 {name}\n"
        "📚 Course: {course_name}\n\n"
        "💰 Balance: {balance} 🪙\n"
        "📈 Savings: {savings} 🪙\n"
        "📉 Loans: {loan} 🪙"
    ),  # Overview of participant balances

    # Inline Keyboard Buttons
    "button_withdraw_cash": "💰 Withdraw Cash",
    "button_deposit_cash": "🏦 Deposit Cash",
    "button_to_savings": "📥 To Savings",
    "button_from_savings": "📤 From Savings",
    "button_take_loan": "💳 Take Loan",
    "button_repay_loan": "💵 Repay Loan",
    "button_cancel": "❌ Cancel",

    # endregion --- Participant Panel ---

    # region --- Withdraw and Deposit Flows ---

    "withdraw_amount_request": "Enter the amount to withdraw (🪙):",
    "deposit_amount_request": "Enter the amount to deposit (🪙):",

    "invalid_amount": "Please enter a valid positive number.",
    "insufficient_funds": "You have insufficient funds.",

    "withdraw_waiting_approval": "Your withdrawal request of {amount} 🪙 is pending operator approval.",
    "deposit_waiting_approval": "Your deposit request of {amount} 🪙 is pending operator approval.",

    "withdraw_cancelled": "Your withdrawal request has been cancelled.",
    "deposit_cancelled": "Your deposit request has been cancelled.",

    # region --- Withdraw and Deposit Flows ---

}
