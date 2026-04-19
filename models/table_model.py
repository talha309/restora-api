# restora-api/models/table_model.py
from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Date, Time
from typing import TYPE_CHECKING
import enum
from db.database import Base

if TYPE_CHECKING:
    from models.order_model import Order


class Status(enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"


class StatusCustomer(enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"


class Table(Base):
    __tablename__ = 'tables'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    table_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)

    # one table has many orders
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="table")

    # one table has many reservations
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="table")


class Reservation(Base):
    __tablename__ = 'reservations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey('tables.id'), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(50), nullable=False)
    guests_count: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False)   # YYYY-MM-DD
    time: Mapped[str] = mapped_column(String(10), nullable=False)   # HH:MM
    status: Mapped[StatusCustomer] = mapped_column(Enum(StatusCustomer), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    # many reservations belong to one table
    table: Mapped["Table"] = relationship("Table", back_populates="reservations")
