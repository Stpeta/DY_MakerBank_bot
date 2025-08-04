from sqlalchemy import (
    Column, Integer, BigInteger, String,
    Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
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
    balance = Column(BigInteger, default=0)
    course = relationship("Course", back_populates="participants")