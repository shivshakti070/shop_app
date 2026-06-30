from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/daily-sales",
    tags=["daily_sales"],
)

@router.get("/", response_model=List[schemas.DailySaleOut])
def read_daily_sales(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    sales = db.query(models.DailySale).filter(models.DailySale.owner_id == current_user.id).all()
    return sales

@router.post("/", response_model=schemas.DailySaleOut)
def create_daily_sale(sale: schemas.DailySaleCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify the item exists in inventory
    inv_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.item == sale.item_name,
        models.InventoryItem.owner_id == current_user.id
    ).first()

    if not inv_item:
        raise HTTPException(status_code=400, detail="Item not found in inventory. Please match exact name.")
    
    if inv_item.remaining_quantity < sale.quantity:
        raise HTTPException(status_code=400, detail=f"Not enough stock. Only {inv_item.remaining_quantity} left.")

    # Deduct stock
    inv_item.remaining_quantity -= sale.quantity
    
    # Snapshot original purchase rate to guarantee persistent profit margin calculation
    sale.purchase_rate_at_sale = inv_item.purchase_rate
    
    db_sale = models.DailySale(**sale.dict(), owner_id=current_user.id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.put("/{sale_id}", response_model=schemas.DailySaleOut)
def update_daily_sale(sale_id: int, sale_update: schemas.DailySaleCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_sale = db.query(models.DailySale).filter(models.DailySale.id == sale_id, models.DailySale.owner_id == current_user.id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
        
    inv_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.item == db_sale.item_name,
        models.InventoryItem.owner_id == current_user.id
    ).first()
    
    if inv_item:
        quantity_delta = sale_update.quantity - db_sale.quantity
        if inv_item.remaining_quantity < quantity_delta:
            raise HTTPException(status_code=400, detail="Not enough stock to update to this quantity.")
        inv_item.remaining_quantity -= quantity_delta
        # Resnapshot the rate in case it changed
        sale_update.purchase_rate_at_sale = inv_item.purchase_rate

    for key, value in sale_update.dict().items():
        setattr(db_sale, key, value)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.delete("/{sale_id}")
def delete_daily_sale(sale_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_sale = db.query(models.DailySale).filter(models.DailySale.id == sale_id, models.DailySale.owner_id == current_user.id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
        
    # Refund Inventory
    inv_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.item == db_sale.item_name,
        models.InventoryItem.owner_id == current_user.id
    ).first()
    if inv_item:
        inv_item.remaining_quantity += db_sale.quantity

    db.delete(db_sale)
    db.commit()
    return {"ok": True}
