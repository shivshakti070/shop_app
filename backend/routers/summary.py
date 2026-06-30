from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/summary",
    tags=["summary"],
)

@router.get("/", response_model=schemas.SummaryOut)
def get_summary(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Calculate Total Inventory Investment
    inventory_items = db.query(models.InventoryItem).filter(
        models.InventoryItem.owner_id == current_user.id
    ).all()
    
    total_investment = sum(item.initial_quantity * item.purchase_rate for item in inventory_items)
    
    # Use standardized YYYY-MM-DD logic
    today_js_format = datetime.now().strftime("%Y-%m-%d")
    
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_js_format = yesterday.strftime("%Y-%m-%d")
    
    todays_sales = db.query(models.DailySale).filter(
        models.DailySale.owner_id == current_user.id,
        models.DailySale.date == today_js_format
    ).all()
    
    yesterdays_sales = db.query(models.DailySale).filter(
        models.DailySale.owner_id == current_user.id,
        models.DailySale.date == yesterday_js_format
    ).all()

    total_todays_sales = sum(sale.total_amount for sale in todays_sales)
    total_yesterdays_sales = sum(sale.total_amount for sale in yesterdays_sales)

    # Calculate Liquidity Balances
    investments = db.query(models.Investment).filter(models.Investment.owner_id == current_user.id).all()
    daily_expenses = db.query(models.DailyExpense).filter(models.DailyExpense.owner_id == current_user.id).all()
    one_time_expenses = db.query(models.OneTimeExpense).filter(models.OneTimeExpense.owner_id == current_user.id).all()

    cash_balance = 0.0
    upi_balance = 0.0
    total_credit = 0.0
    total_profit = 0.0

    # Calculate Total Profit and fetch all sales for liquidity
    all_sales = db.query(models.DailySale).filter(models.DailySale.owner_id == current_user.id).all()
    for sale in all_sales:
        profit = (sale.price_per_unit - sale.purchase_rate_at_sale) * sale.quantity
        total_profit += profit

    # Add Investments
    for inv in investments:
        if inv.payment_method == "Cash": cash_balance += inv.amount
        elif inv.payment_method == "UPI": upi_balance += inv.amount

    # Add Sales & Track Credit
    for sale in all_sales:
        if sale.payment_method == "Cash": cash_balance += sale.total_amount
        elif sale.payment_method == "UPI": upi_balance += sale.total_amount
        elif sale.payment_method == "Credit": total_credit += sale.total_amount

    # Subtract Expenses
    for exp in daily_expenses:
        if exp.payment_method == "Cash": cash_balance -= exp.amount
        elif exp.payment_method == "UPI": upi_balance -= exp.amount

    # Subtract One-Time Expenses
    for exp in one_time_expenses:
        if exp.payment_method == "Cash": cash_balance -= exp.amount
        elif exp.payment_method == "UPI": upi_balance -= exp.amount

    return schemas.SummaryOut(
        total_inventory_investment=total_investment,
        todays_sales=total_todays_sales,
        yesterdays_sales=total_yesterdays_sales,
        total_profit=total_profit,
        cash_balance=cash_balance,
        upi_balance=upi_balance,
        total_outstanding_credit=total_credit
    )
