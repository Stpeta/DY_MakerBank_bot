from datetime import datetime

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
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    finish_date = Column(DateTime, nullable=True)

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

    # Main wallet balance (coins available)
    balance = Column(BigInteger, default=0)

    # Savings account balance; accrues weekly interest
    savings_balance = Column(BigInteger, default=0)
    last_savings_deposit_at = Column(DateTime, nullable=True)  # timestamp of last savings contribution

    # Loan account balance; accrues weekly interest
    loan_balance = Column(BigInteger, default=0)

    course = relationship("Course", back_populates="participants")


# Table to record changes in savings and loan interest rates
class RateHistory(Base):
    __tablename__ = "rate_history"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    kind = Column(Enum("savings", "loan", name="rate_kind"), nullable=False)  # 'savings' or 'loan'
    rate = Column(Numeric(5, 2), nullable=False)  # weekly interest rate as percentage
    set_at = Column(DateTime, default=datetime.utcnow)  # timestamp when rate was set


# Table to record all financial transactions and status
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), index=True, nullable=False)

    type = Column(Enum(
        # Cash operations
        "cash_withdrawal", "cash_deposit",
        # Savings account operations
        "savings_deposit",  # move coins into savings
        "savings_withdraw",  # move coins out of savings
        "savings_interest",  # interest credit on savings
        # Loan account operations
        "loan_borrow",  # take out a loan
        "loan_repay",  # repay a loan
        "loan_interest",  # interest debit on loan
        # Operator adjustments
        "operator_adjustment",
        name="tx_type"
    ), nullable=False)

    amount = Column(Numeric, nullable=False)

    status = Column(Enum(
        "pending", "completed", "declined", "canceled",
        name="tx_status"
    ), default="pending", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    participant = relationship("Participant", backref="transactions")
