# TableCreate, ReservationCreate, ReservationOut
# TableCreate     → table_number, capacity, location
# TableOut        → id, table_number, capacity, status, location
# TableStatusUpdate → status    ← just for PATCH

# 📅 Reservation Schemas
# ReservationCreate → customer_name, customer_phone, guests_count, date, time, table_id
# ReservationOut    → id, customer_name, date, time, status, table_id, created_at
# ReservationUpdate → status    ← confirm or cancel

from pydantic import BaseModel
from typing import Optional

class TableCreate(BaseModel):
    table_number: int
    capacity: int
    location: str
class TableOut(BaseModel):
    id: int
    table_number: int
    capacity: int
    status: str
    location: str
class TableStatusUpdate(BaseModel):
    status: str

class ReservationCreate(BaseModel):
    customer_name: str
    customer_phone: str
    guests_count: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    table_id: int

class ReservationOut(BaseModel):
    id: int
    customer_name: str
    date: str
    time: str
    status: str
    table_id: int
    created_at: str

class ReservationUpdate(BaseModel):
    status: str