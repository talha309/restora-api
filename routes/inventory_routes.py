from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.inventory_model import InventoryItem
from schemas.inventory_schema import InventoryCreate, InventoryUpdate, InventoryOut
from utils.auth_util import get_current_user
from datetime import datetime

router = APIRouter()


# ────────────────────────────────────────────
# CREATE INVENTORY ITEM
# ────────────────────────────────────────────

@router.post("/", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    item: InventoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    existing = db.query(InventoryItem).filter(InventoryItem.name == item.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{item.name}' already exists in inventory. "
                   f"You can update its quantity instead. 📦"
        )

    new_item = InventoryItem(**item.model_dump(), last_updated=datetime.utcnow())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# ────────────────────────────────────────────
# GET ALL INVENTORY ITEMS
# ────────────────────────────────────────────

@router.get("/", response_model=list[InventoryOut])
def get_all_inventory(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(InventoryItem).all()


# ────────────────────────────────────────────
# GET SINGLE INVENTORY ITEM
# ────────────────────────────────────────────

@router.get("/{id}", response_model=InventoryOut)
def get_inventory_item(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(InventoryItem.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return item


# ────────────────────────────────────────────
# INCREMENT STOCK
# ────────────────────────────────────────────

@router.patch("/{id}/increment", response_model=InventoryOut)
def increment_stock(
    id: int,
    updated: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    # quantity field required check
    if updated.quantity is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quantity field is required for increment. 📦"
        )

    item = db.query(InventoryItem).filter(InventoryItem.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    item.quantity += updated.quantity
    item.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(item)
    return item


# ────────────────────────────────────────────
# DECREMENT STOCK
# ────────────────────────────────────────────

@router.patch("/{id}/decrement", response_model=InventoryOut)
def decrement_stock(
    id: int,
    updated: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    # quantity field required check
    if updated.quantity is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quantity field is required for decrement. 📦"
        )

    item = db.query(InventoryItem).filter(InventoryItem.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    # negative stock check → beautiful message
    if item.quantity - updated.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Oops! You only have {item.quantity} {item.unit} of '{item.name}' left. "
                   f"Cannot deduct {updated.quantity} {item.unit}. Please restock first. 🛒"
        )

    item.quantity -= updated.quantity
    item.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(item)
    return item


# ────────────────────────────────────────────
# UPDATE INVENTORY ITEM DETAILS
# ────────────────────────────────────────────

@router.put("/{id}", response_model=InventoryOut)
def update_inventory_item(
    id: int,
    updated: InventoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    item = db.query(InventoryItem).filter(InventoryItem.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    for field, value in updated.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    item.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(item)
    return item


# ────────────────────────────────────────────
# LOW STOCK ALERTS
# ────────────────────────────────────────────

@router.get("/alerts/low-stock")
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "waiter"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Waiter only")

    low_items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.minimum_stock
    ).all()

    if not low_items:
        return {"message": "All stocks are at healthy levels. Nothing to worry about! ✅"}

    alerts = []
    for item in low_items:
        if item.quantity == 0:
            msg = f"🚨 '{item.name}' is completely OUT OF STOCK! Please reorder immediately."
        else:
            msg = (f"⚠️ '{item.name}' is running low — only {item.quantity} {item.unit} left. "
                   f"Minimum required: {item.minimum_stock} {item.unit}.")

        alerts.append({
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "minimum_stock": item.minimum_stock,
            "unit": item.unit,
            "message": msg
        })

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }


# ────────────────────────────────────────────
# DELETE INVENTORY ITEM
# ────────────────────────────────────────────

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    item = db.query(InventoryItem).filter(InventoryItem.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    db.delete(item)
    db.commit()