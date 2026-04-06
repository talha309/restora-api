# user_model.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum
import enum
from db.database import Base
from models.order_model import Order  


class Role(enum.Enum):
    admin = "admin"
    waiter = "waiter"
    kitchen = "kitchen"
    customer = "customer"


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    # one waiter handles many orders
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="waiter")
# one waiter handles many orders 

# uv run alembic revision --autogenerate -m "design tables inventory,menu,order,table,user"
# uv run alembic upgrade head