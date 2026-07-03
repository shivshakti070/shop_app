from fastapi import APIRouter, Depends, HTTPException
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
def read_daily_sales(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(models.DailySale)
        .filter(models.DailySale.owner_id == current_user.id)
        .order_by(models.DailySale.date.desc(), models.DailySale.id.desc())
        .all()
    )


@router.post("/", response_model=schemas.DailySaleOut)
def create_daily_sale(
    sale: schemas.DailySaleCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    inv_item = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id == sale.inventory_item_id,
            models.InventoryItem.owner_id == current_user.id
        )
        .first()
    )

    if not inv_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if inv_item.remaining_quantity < sale.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {inv_item.remaining_quantity} item(s) available."
        )

    inv_item.remaining_quantity -= sale.quantity

    db_sale = models.DailySale(
        date=sale.date,
        inventory_item_id=inv_item.id,
        item_name=inv_item.item,
        brand=inv_item.brand,
        quantity=sale.quantity,
        price_per_unit=sale.price_per_unit,
        total_amount=sale.total_amount,
        purchase_rate_at_sale=inv_item.purchase_rate,
        payment_method=sale.payment_method,
        customer_name=sale.customer_name,
        owner_id=current_user.id,
    )

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    return db_sale


@router.put("/{sale_id}", response_model=schemas.DailySaleOut)
def update_daily_sale(
    sale_id: int,
    sale: schemas.DailySaleCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_sale = (
        db.query(models.DailySale)
        .filter(
            models.DailySale.id == sale_id,
            models.DailySale.owner_id == current_user.id
        )
        .first()
    )

    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    old_inventory = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id == db_sale.inventory_item_id,
            models.InventoryItem.owner_id == current_user.id
        )
        .first()
    )

    if old_inventory:
        old_inventory.remaining_quantity += db_sale.quantity

    new_inventory = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id == sale.inventory_item_id,
            models.InventoryItem.owner_id == current_user.id
        )
        .first()
    )

    if not new_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if new_inventory.remaining_quantity < sale.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {new_inventory.remaining_quantity} item(s) available."
        )

    new_inventory.remaining_quantity -= sale.quantity

    db_sale.date = sale.date
    db_sale.inventory_item_id = new_inventory.id
    db_sale.item_name = new_inventory.item
    db_sale.brand = new_inventory.brand
    db_sale.quantity = sale.quantity
    db_sale.price_per_unit = sale.price_per_unit
    db_sale.total_amount = sale.total_amount
    db_sale.purchase_rate_at_sale = new_inventory.purchase_rate
    db_sale.payment_method = sale.payment_method
    db_sale.customer_name = sale.customer_name

    db.commit()
    db.refresh(db_sale)

    return db_sale


@router.delete("/{sale_id}")
def delete_daily_sale(
    sale_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_sale = (
        db.query(models.DailySale)
        .filter(
            models.DailySale.id == sale_id,
            models.DailySale.owner_id == current_user.id
        )
        .first()
    )

    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    inv_item = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id == db_sale.inventory_item_id,
            models.InventoryItem.owner_id == current_user.id
        )
        .first()
    )

    if inv_item:
        inv_item.remaining_quantity += db_sale.quantity

    db.delete(db_sale)
    db.commit()

    return {"ok": True}