# models/menu_model.py
# 

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from db.database import Base
from models.order_model import OrderItem  # ✅ Import OrderItem for relationship



class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # one category has many menu items
    menu_items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(nullable=False, default=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    # many menu items belong to one category
    category: Mapped["Category"] = relationship("Category", back_populates="menu_items")

    # one menu item appears in many order items
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="menu_item")

# one menu item appears in many order items
# one category has many menu items