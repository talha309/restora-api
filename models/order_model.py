# order_model.py
# Order + OrderItem tables
# id              → Integer, primary key
# status          → Enum → "pending", "preparing", "ready", "served", "cancelled"
# total_price     → Float, default = 0
# notes           → String, nullable
# table_id        → ForeignKey → Table.id
# waiter_id       → ForeignKey → User.id
# created_at      → DateTime, default = now
# updated_at      → DateTime, auto-updates

# 🛒 OrderItem
# id              → Integer, primary key
# quantity        → Integer, not null
# unit_price      → Float, not null      ← price copy at time of order
# subtotal        → Float, not null      ← quantity × unit_price
# order_id        → ForeignKey → Order.id
# menu_item_id    → ForeignKey → MenuItem.id

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey, Enum, Table  # ✅ Table removed
import enum
from db.database import Base
from models.table_model import Table  # ✅ Import Table for relationship
from models.user_model import User  # ✅ Import User for relationship
from models.menu_model import MenuItem  # ✅ Import MenuItem for relationship
# ✅ No model imports needed — relationships use string references


class OrderStatus(enum.Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    served = "served"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str] = mapped_column(String(255), nullable=True)
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey('tables.id'), nullable=False)
    waiter_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    # many orders belong to one table
    table: Mapped["Table"] = relationship("Table", back_populates="orders")

    # many orders handled by one waiter (User)
    waiter: Mapped["User"] = relationship("User", back_populates="orders")

    # one order has many order items
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)
    menu_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('menu_items.id'), nullable=False)

    # many order items belong to one order
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    # many order items reference one menu item
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_items")