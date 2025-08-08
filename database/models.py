from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, BigInteger, String,
    Boolean, ForeignKey, DateTime, Numeric, Enum
)
from sqlalchemy.orm import relationship

from database.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    sheet_url = Column(String, nullable=True)
    creator_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    finish_date = Column(DateTime, nullable=True)

    # Course-wide financial settings
    max_loan_amount = Column(Numeric(8, 2), default=100)  # maximum total loan per participant
    savings_withdrawal_delay = Column(Integer, default=7)  # days lock after deposit
    interest_day = Column(Integer, default=0)  # 0=Monday ... 6=Sunday
    interest_time = Column(String, default="09:00")  # HH:MM in UTC

    # Relationship to participants
    participants = relationship("Participant", back_populates="course")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    registration_code = Column(String(6), unique=True, nullable=False)
    telegram_id = Column(BigInteger, nullable=True)
    is_registered = Column(Boolean, default=False)

    # Balances support 2 decimal places, up to 6 digits before the point
    balance = Column(Numeric(8, 2), default=0)
    savings_balance = Column(Numeric(8, 2), default=0)
    loan_balance = Column(Numeric(8, 2), default=0)

    # timestamp of last deposit to savings to enforce withdrawal delay
    last_savings_deposit_at = Column(DateTime(timezone=True), nullable=True)

    course = relationship("Course", back_populates="participants")
    transactions = relationship("Transaction", back_populates="participant")


# Table to record changes in savings and loan interest rates
class RateHistory(Base):
    __tablename__ = "rate_history"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    kind = Column(Enum("savings", "loan", name="rate_kind"), nullable=False)  # 'savings' or 'loan'
    rate = Column(Numeric(5, 2), nullable=False)  # weekly interest rate as percentage
    set_at = Column(DateTime, default=datetime.now(timezone.utc))  # timestamp when rate was set


# Table to record all financial transactions and status
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), index=True, nullable=False)

    type = Column(Enum(
        "cash_withdrawal", "cash_deposit",
        "savings_deposit", "savings_withdraw", "savings_interest",
        "loan_borrow", "loan_repay", "loan_interest",
        "operator_adjustment",
        name="tx_type"
    ), nullable=False)

    # Amount also two decimals
    amount = Column(Numeric(8, 2), nullable=False)

    status = Column(Enum(
        "pending", "completed", "declined", "canceled",
        name="tx_status"
    ), default="pending", nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)

    participant = relationship("Participant", back_populates="transactions")
