 # restora-api/schemas/order_schema.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int


class OrderCreate(BaseModel):
    table_id: int
    notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    quantity: int
    unit_price: float
    subtotal: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total_price: float
    table_id: int
    waiter_id: int
    created_at: datetime
    items: List[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: str   # "pending" | "preparing" | "ready" | "served" | "cancelled"