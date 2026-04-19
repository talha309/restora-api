# restora-api/routes/order_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db                          # ✅ fixed: was database.database
from models.order_model import Order, OrderItem, OrderStatus
from models.table_model import Table
from models.menu_model import MenuItem
from schemas.order_schema import OrderCreate, OrderOut, OrderStatusUpdate
from utils.auth_util import get_current_user            # ✅ fixed: was auth_utils
from datetime import datetime

router = APIRouter()


# ────────────────────────────────────────────
# CREATE ORDER
# ────────────────────────────────────────────

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    # check table exists
    table = db.query(Table).filter(Table.id == order.table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    now = datetime.utcnow()

    # create order
    new_order = Order(
    table_id=order.table_id,
    waiter_id=current_user.id,
    notes=order.notes,
    status=OrderStatus.pending,
    total_price=0,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
    db.add(new_order)
    db.flush()  # get new_order.id before commit

    total = 0

    for item in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()

        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with id {item.menu_item_id} not found"
            )

        if not menu_item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sorry! '{menu_item.name}' is currently not available. "
                       f"Please choose another item from our menu. 🍽️"
            )

        unit_price = menu_item.price
        subtotal = unit_price * item.quantity

        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
        db.add(order_item)
        total += subtotal

    new_order.total_price = total

    # auto update table status → occupied
    table.status = "occupied"

    db.commit()
    db.refresh(new_order)
    return new_order


# ────────────────────────────────────────────
# GET ALL ORDERS → role based filter
# ────────────────────────────────────────────

@router.get("/", response_model=list[OrderOut])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(Order).all()

    elif current_user.role == "waiter":
        return db.query(Order).filter(Order.waiter_id == current_user.id).all()

    elif current_user.role == "kitchen":
        return db.query(Order).filter(
            Order.status.in_([OrderStatus.pending, OrderStatus.preparing])
        ).all()

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ────────────────────────────────────────────
# GET ACTIVE ORDERS BY TABLE  (must be before /{id})
# ────────────────────────────────────────────

@router.get("/table/{table_id}", response_model=list[OrderOut])
def get_orders_by_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    orders = db.query(Order).filter(
        Order.table_id == table_id,
        Order.status.in_([OrderStatus.pending, OrderStatus.preparing, OrderStatus.ready])
    ).all()

    return orders


# ────────────────────────────────────────────
# GET SINGLE ORDER
# ────────────────────────────────────────────

@router.get("/{id}", response_model=OrderOut)
def get_order(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


# ────────────────────────────────────────────
# UPDATE ORDER STATUS
# ────────────────────────────────────────────

@router.patch("/{id}/status", response_model=OrderOut)
def update_order_status(
    id: int,
    updated: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Validate status value
    valid_statuses = [s.value for s in OrderStatus]
    if updated.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    if updated.status == "cancelled":
        if current_user.role not in ["admin", "waiter"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Waiter can cancel an order"
            )
        table = db.query(Table).filter(Table.id == order.table_id).first()
        if table:
            table.status = "available"

    if updated.status == "served":
        table = db.query(Table).filter(Table.id == order.table_id).first()
        if table:
            table.status = "available"

    order.status = OrderStatus(updated.status)
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


# ────────────────────────────────────────────
# DELETE ORDER
# ────────────────────────────────────────────

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    table = db.query(Table).filter(Table.id == order.table_id).first()
    if table:
        table.status = "available"

    db.delete(order)
    db.commit()