from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    db_item = models.InventoryItem(**item.dict(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=schemas.InventoryOut)
def update_inventory_item(item_id: int, item_update: schemas.InventoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id, models.InventoryItem.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item_update.dict().items():
        setattr(db_item, key, value)
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
