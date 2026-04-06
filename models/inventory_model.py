# inventory_model.py
# InventoryItem table
# id  → Integer, primary key
# name          → String, unique, not null   (e.g. "Chicken")
# quantity      → Float, not null            (current stock)
# unit          → String, not null           (e.g. "kg", "liters")
# minimum_stock → Float, not null            ← alert threshold
# last_updated  → DateTime, auto-updates

from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Float
from db.database import Base

class InventoryItem(Base):
    __tablename__ = 'inventory_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    minimum_stock: Mapped[float] = mapped_column(Float, nullable=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime, nullable=False)