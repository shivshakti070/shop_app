from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/sales-returns",
    tags=["Sales Returns"],
)

@router.get("/", response_model=list[schemas.SalesReturnOut])
def read_sales_returns(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.SalesReturn)
        .filter(models.SalesReturn.owner_id == current_user.id)
        .order_by(models.SalesReturn.date.desc())
        .all()
    )

@router.post("/", response_model=schemas.SalesReturnOut)
def create_sales_return(
    payload: schemas.SalesReturnCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    sale = db.query(models.DailySale).filter(
        models.DailySale.id == payload.sale_id,
        models.DailySale.owner_id == current_user.id
    ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    inventory = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == sale.inventory_item_id,
        models.InventoryItem.owner_id == current_user.id
    ).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    if payload.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid quantity"
        )

    # ----------------------------
    # Calculate already returned quantity
    # ----------------------------
    total_returned = sum(r.quantity for r in sale.returns)

    remaining_returnable = sale.quantity - total_returned

    if payload.quantity > remaining_returnable:
        raise HTTPException(
            status_code=400,
            detail=f"Only {remaining_returnable} item(s) can still be returned."
        )

    refund = models.SalesReturn(
        date=payload.date,
        sale_id=sale.id,
        inventory_id=inventory.id,
        quantity=payload.quantity,
        refund_amount=payload.refund_amount,
        reason=payload.reason,
        owner_id=current_user.id
    )

    db.add(refund)

    # Add stock back
    inventory.remaining_quantity += payload.quantity

    return_sale = models.DailySale(
        date=payload.date,
        inventory_item_id=inventory.id,
        item_name=inventory.item,
        brand=inventory.brand,
        quantity=-payload.quantity,
        price_per_unit=sale.price_per_unit,
        total_amount=-payload.refund_amount,
        purchase_rate_at_sale=inventory.purchase_rate,
        payment_method=f"RETURN ({sale.payment_method})",
        customer_name=sale.customer_name,
        owner_id=current_user.id
    )

    db.add(return_sale)
    # If original sale was on Credit,
    # reduce the outstanding credit amount.

    # DO NOT MODIFY THE ORIGINAL SALE

    db.commit()
    db.refresh(refund)

    return refund