# InventoryCreate, InventoryOut , inventory_update
# InventoryCreate → name, quantity, unit, minimum_stock
# InventoryUpdate → quantity?, minimum_stock?    ← optional
# InventoryOut    → id, name, quantity, unit, minimum_stock, last_updated

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InventoryCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    minimum_stock: float

class InventoryUpdate(BaseModel):
    quantity: float | None = None
    minimum_stock: float | None = None

class InventoryOut(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str
    minimum_stock: float
    last_updated: datetime

