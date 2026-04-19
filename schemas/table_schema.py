 # restora-api/schemas/table_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TableCreate(BaseModel):
    table_number: int
    capacity: int
    location: Optional[str] = None


class TableOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    table_number: int
    capacity: int
    status: str
    location: Optional[str] = None


class TableStatusUpdate(BaseModel):
    status: str   # "available" | "occupied" | "reserved"


class ReservationCreate(BaseModel):
    customer_name: str
    customer_phone: str
    guests_count: int
    date: str   # YYYY-MM-DD
    time: str   # HH:MM
    table_id: int


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_phone: str
    guests_count: int
    date: str
    time: str
    status: str
    table_id: int
    created_at: datetime


class ReservationUpdate(BaseModel):
    status: str   # "confirmed" | "cancelled"