from aiogram.fsm.state import StatesGroup, State


class CourseCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_savings_rate = State()
    waiting_for_loan_rate = State()
    waiting_for_admin_email = State()


class CourseEdit(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_interest_day = State()
    waiting_for_interest_time = State()
    waiting_for_savings_rate = State()
    waiting_for_loan_rate = State()
    waiting_for_max_loan = State()
    waiting_for_savings_lock = State()


class Registration(StatesGroup):
    waiting_for_code = State()


class CourseFinish(StatesGroup):
    waiting_for_course = State()


class CashOperations(StatesGroup):
    waiting_for_withdraw_amount = State()
    waiting_for_deposit_amount = State()
    waiting_for_savings_deposit_amount = State()
    waiting_for_savings_withdraw_amount = State()
    waiting_for_take_loan_amount = State()
    waiting_for_repay_loan_amount = State()
    waiting_for_approval = State()

