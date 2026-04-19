# restora-api/models/inventory_model.py
from sqlalchemy.orm import Mapped, mapped_column
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