# table_model.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey
import enum
from db.database import Base
from models.order_model import Order  # ✅ Import Order for relationship



class Status(enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"


class Status_Customer(enum.Enum):
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
    reservation_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    status: Mapped[Status_Customer] = mapped_column(Enum(Status_Customer), nullable=False)

    # many reservations belong to one table
    table: Mapped["Table"] = relationship("Table", back_populates="reservations")
# one table has many orders
