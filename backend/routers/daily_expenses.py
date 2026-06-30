from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/daily-expenses",
    tags=["daily_expenses"],
)

@router.get("/", response_model=List[schemas.DailyExpenseOut])
def read_daily_expenses(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    expenses = db.query(models.DailyExpense).filter(models.DailyExpense.owner_id == current_user.id).all()
    return expenses

@router.post("/", response_model=schemas.DailyExpenseOut)
def create_daily_expense(expense: schemas.DailyExpenseCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_expense = models.DailyExpense(**expense.dict(), owner_id=current_user.id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.put("/{expense_id}", response_model=schemas.DailyExpenseOut)
def update_daily_expense(expense_id: int, expense_update: schemas.DailyExpenseCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_expense = db.query(models.DailyExpense).filter(models.DailyExpense.id == expense_id, models.DailyExpense.owner_id == current_user.id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for key, value in expense_update.dict().items():
        setattr(db_expense, key, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/{expense_id}")
def delete_daily_expense(expense_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_expense = db.query(models.DailyExpense).filter(models.DailyExpense.id == expense_id, models.DailyExpense.owner_id == current_user.id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(db_expense)
    db.commit()
    return {"ok": True}
