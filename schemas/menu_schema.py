# CategoryCreate, MenuItemCreate, MenuItemOut
# CategoryCreate  → name, description
# CategoryOut     → id, name, description
# 🍔 MenuItem Schemas
# MenuItemCreate  → name, description, price, is_available, category_id
# MenuItemUpdate  → name?, description?, price?, is_available?   ← all optional
# MenuItemOut     → id, name, price, is_available, category_id, created_at

from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool
    category_id: int

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

class MenuItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool
    category_id: int
    created_at: str