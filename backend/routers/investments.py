from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/investments",
    tags=["investments"],
)

@router.get("/", response_model=List[schemas.InvestmentOut])
def read_investments(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    investments = db.query(models.Investment).filter(models.Investment.owner_id == current_user.id).all()
    return investments

@router.post("/", response_model=schemas.InvestmentOut)
def create_investment(investment: schemas.InvestmentCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if a source with the exact same name already exists for this user
    existing_investment = db.query(models.Investment).filter(
        models.Investment.source == investment.source, 
        models.Investment.owner_id == current_user.id
    ).first()

    if existing_investment:
        existing_investment.amount += investment.amount
        # optionally update notes or date
        existing_investment.date = investment.date 
        db.commit()
        db.refresh(existing_investment)
        return existing_investment
    else:
        db_investment = models.Investment(**investment.dict(), owner_id=current_user.id)
        db.add(db_investment)
        db.commit()
        db.refresh(db_investment)
        return db_investment

@router.put("/{investment_id}", response_model=schemas.InvestmentOut)
def update_investment(investment_id: int, investment_update: schemas.InvestmentCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_investment = db.query(models.Investment).filter(models.Investment.id == investment_id, models.Investment.owner_id == current_user.id).first()
    if not db_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    for key, value in investment_update.dict().items():
        setattr(db_investment, key, value)
    db.commit()
    db.refresh(db_investment)
    return db_investment

@router.delete("/{investment_id}")
def delete_investment(investment_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_investment = db.query(models.Investment).filter(models.Investment.id == investment_id, models.Investment.owner_id == current_user.id).first()
    if not db_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    db.delete(db_investment)
    db.commit()
    return {"ok": True}
