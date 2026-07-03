from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

@router.get("/", response_model=List[schemas.InventoryOut])
def read_inventory(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(models.InventoryItem).filter(models.InventoryItem.owner_id == current_user.id).all()
    return items

@router.post("/", response_model=schemas.InventoryOut)
def create_inventory_item(item: schemas.InventoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    item_name = item.item.strip()
    brand_name = item.brand.strip()
    incoming_quantity = item.initial_quantity

    if incoming_quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    db_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.owner_id == current_user.id,
        func.lower(models.InventoryItem.item) == item_name.lower(),
        func.lower(models.InventoryItem.brand) == brand_name.lower(),
    ).first()

    if db_item:
        old_total_value = db_item.initial_quantity * db_item.purchase_rate
        new_total_value = incoming_quantity * item.purchase_rate
        new_total_quantity = db_item.initial_quantity + incoming_quantity

        db_item.date = item.date
        db_item.initial_quantity = new_total_quantity
        db_item.remaining_quantity += incoming_quantity
        db_item.purchase_rate = (old_total_value + new_total_value) / new_total_quantity
        db.commit()
        db.refresh(db_item)
        return db_item

    db_item = models.InventoryItem(
        date=item.date,
        item=item_name,
        brand=brand_name,
        initial_quantity=incoming_quantity,
        remaining_quantity=incoming_quantity,
        purchase_rate=item.purchase_rate,
        owner_id=current_user.id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=schemas.InventoryOut)
def update_inventory_item(item_id: int, item_update: schemas.InventoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id, models.InventoryItem.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item_update.initial_quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    sold_quantity = max(db_item.initial_quantity - db_item.remaining_quantity, 0)
    if item_update.initial_quantity < sold_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Quantity cannot be less than already sold quantity ({sold_quantity})",
        )

    db_item.date = item_update.date
    db_item.item = item_update.item.strip()
    db_item.brand = item_update.brand.strip()
    db_item.initial_quantity = item_update.initial_quantity
    db_item.remaining_quantity = item_update.initial_quantity - sold_quantity
    db_item.purchase_rate = item_update.purchase_rate

    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_inventory_item(item_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id, models.InventoryItem.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}
