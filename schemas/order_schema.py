# OrderCreate, OrderItemCreate, OrderOut
# OrderItemCreate → menu_item_id, quantity
# OrderCreate     → table_id, notes?, items: List[OrderItemCreate]
# OrderOut        → id, status, total_price, table_id, waiter_id, created_at
# OrderItemOut    → id, menu_item_id, quantity, unit_price, subtotal
# OrderStatusUpdate → status

from pydantic import BaseModel
from typing import List, Optional

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    
class OrderCreate(BaseModel):
    table_id: int
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    unit_price: float
    subtotal: float

class OrderOut(BaseModel):
    id: int
    status: str
    total_price: float
    table_id: int
    waiter_id: int
    created_at: str
    items: List[OrderItemOut]

class OrderStatusUpdate(BaseModel):
    status: str