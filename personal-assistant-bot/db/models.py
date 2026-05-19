from sqlalchemy import (
    Column, Integer, Text, Boolean, Date, Time, TIMESTAMP,
    ForeignKey, ARRAY
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    emoji = Column(Text)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tasks = relationship("Task", back_populates="business")
    routines = relationship("Routine", back_populates="business")
    notes = relationship("Note", back_populates="business")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    due_time = Column(Time)
    priority = Column(Text, default="normal")  # low | normal | high
    status = Column(Text, default="pending")   # pending | done | cancelled
    created_at = Column(TIMESTAMP, server_default=func.now())
    done_at = Column(TIMESTAMP)

    business = relationship("Business", back_populates="tasks")


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    title = Column(Text, nullable=False)
    frequency = Column(Text, nullable=False)  # daily | weekly | monthly
    weekdays = Column(Text)                   # "1,3,5" = seg/qua/sex
    remind_time = Column(Time)
    active = Column(Boolean, default=True)
    last_done = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.now())

    business = relationship("Business", back_populates="routines")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP, server_default=func.now())

    business = relationship("Business", back_populates="notes")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True)
    role = Column(Text, nullable=False)   # user | assistant
    content = Column(Text, nullable=False)
    session_date = Column(Date, server_default=func.current_date())
    created_at = Column(TIMESTAMP, server_default=func.now())
