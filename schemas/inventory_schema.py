# # restora-api/schemas/inventory_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InventoryCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    minimum_stock: float


class InventoryUpdate(BaseModel):
    quantity: Optional[float] = None
    minimum_stock: Optional[float] = None


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    quantity: float
    unit: str
    minimum_stock: float
    last_updated: datetime
