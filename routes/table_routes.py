from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.table_model import Table, Reservation, Status, StatusCustomer
from schemas.table_schema import (
    TableCreate, TableOut,
    ReservationCreate, ReservationOut, ReservationUpdate
)
from utils.auth_util import get_current_user
from datetime import datetime

router = APIRouter()


# ────────────────────────────────────────────
# TABLE ROUTES
# ────────────────────────────────────────────

@router.post("/", response_model=TableOut, status_code=status.HTTP_201_CREATED)
def create_table(
    table: TableCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    existing = db.query(Table).filter(Table.table_number == table.table_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table number already exists")

    new_table = Table(**table.model_dump(), status=Status.available)
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table


@router.get("/", response_model=list[TableOut])
def get_all_tables(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Table).all()


@router.get("/{id}", response_model=TableOut)
def get_table(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    table = db.query(Table).filter(Table.id == id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table


@router.put("/{id}", response_model=TableOut)
def update_table(
    id: int,
    updated: TableCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    table = db.query(Table).filter(Table.id == id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    for field, value in updated.model_dump(exclude_unset=True).items():
        setattr(table, field, value)

    db.commit()
    db.refresh(table)
    return table


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    table = db.query(Table).filter(Table.id == id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    db.delete(table)
    db.commit()


# ────────────────────────────────────────────
# RESERVATION ROUTES
# ────────────────────────────────────────────

@router.post("/reservations", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    # check table exists
    table = db.query(Table).filter(Table.id == reservation.table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    # guests count check → beautiful message
    if reservation.guests_count > table.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No worries! This table holds {table.capacity} guests max. "
                   f"Please choose a bigger table for {reservation.guests_count} guests. 🪑"
        )

    # same table same date+time overlap check → beautiful message
    overlap = db.query(Reservation).filter(
        Reservation.table_id == reservation.table_id,
        Reservation.date == reservation.date,
        Reservation.time == reservation.time,
        Reservation.status != StatusCustomer.cancelled
    ).first()

    if overlap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Oops! Table {table.table_number} is already reserved "
                   f"on {reservation.date} at {reservation.time}. "
                   f"Please pick a different time or table. 📅"
        )

    # create reservation
    new_reservation = Reservation(
        **reservation.model_dump(),
        status=StatusCustomer.confirmed,
        created_at=datetime.utcnow()
    )
    db.add(new_reservation)

    # auto update table status → reserved
    table.status = Status.reserved

    db.commit()
    db.refresh(new_reservation)
    return new_reservation


@router.get("/reservations", response_model=list[ReservationOut])
def get_all_reservations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    return db.query(Reservation).all()


@router.get("/reservations/{id}", response_model=ReservationOut)
def get_reservation(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return reservation


@router.patch("/reservations/{id}", response_model=ReservationOut)
def update_reservation_status(
    id: int,
    updated: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    # validate status value
    valid_statuses = [s.value for s in StatusCustomer]
    if updated.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    reservation.status = StatusCustomer(updated.status)

    # auto update table status → available when cancelled
    if updated.status == "cancelled":
        table = db.query(Table).filter(Table.id == reservation.table_id).first()
        if table:
            table.status = Status.available

    db.commit()
    db.refresh(reservation)
    return reservation


@router.delete("/reservations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    # auto reset table status → available
    table = db.query(Table).filter(Table.id == reservation.table_id).first()
    if table:
        table.status = Status.available

    db.delete(reservation)
    db.commit()