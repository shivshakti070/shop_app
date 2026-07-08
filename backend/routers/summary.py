from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/summary",
    tags=["summary"],
)

def get_date_range(period: str):
    """Return start and end date based on period."""
    today = datetime.now().date()
    
    if period == "daily":
        return today, today
    elif period == "monthly":
        month_start = today.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
        return month_start, month_end
    elif period == "yearly":
        year_start = today.replace(month=1, day=1)
        year_end = today.replace(month=12, day=31)
        return year_start, year_end
    elif period == "lifetime":
        return None, None  # No date range for lifetime
    else:
        return today, today  # Default to daily

def calculate_summary(current_user: models.User, db: Session, period: str = "daily") -> schemas.SummaryOut:
    """Calculate summary metrics for the given period."""
    
    start_date, end_date = get_date_range(period)
    
    # Fetch inventory for inventory value
    inventory_items = db.query(models.InventoryItem).filter(
        models.InventoryItem.owner_id == current_user.id
    ).all()
    inventory_value = sum(item.remaining_quantity * item.purchase_rate for item in inventory_items)
    
    # Build query filters
    sale_filter = [models.DailySale.owner_id == current_user.id]
    if start_date and end_date:
        sale_filter.append(models.DailySale.date >= start_date.isoformat())
        sale_filter.append(models.DailySale.date <= end_date.isoformat())
    
    expense_filter = [models.DailyExpense.owner_id == current_user.id]
    if start_date and end_date:
        expense_filter.append(models.DailyExpense.date >= start_date.isoformat())
        expense_filter.append(models.DailyExpense.date <= end_date.isoformat())
    
    investment_filter = [models.Investment.owner_id == current_user.id]
    if start_date and end_date:
        investment_filter.append(models.Investment.date >= start_date.isoformat())
        investment_filter.append(models.Investment.date <= end_date.isoformat())
    
    one_time_expense_filter = [models.OneTimeExpense.owner_id == current_user.id]
    if start_date and end_date:
        one_time_expense_filter.append(models.OneTimeExpense.date >= start_date.isoformat())
        one_time_expense_filter.append(models.OneTimeExpense.date <= end_date.isoformat())
    
    # Fetch sales data
    sales = db.query(models.DailySale).filter(*sale_filter).all()
    
    # Separate returns and regular sales
    regular_sales = [s for s in sales if not s.is_return]
    returns = [s for s in sales if s.is_return]
    
    # Calculate metrics
    sales_total = sum(s.total_amount for s in regular_sales)
    returns_total = sum(s.total_amount for s in returns)
    net_sales = sales_total - returns_total
    
    # Calculate profit and loss
    profit_total = 0.0
    loss_total = 0.0
    for sale in regular_sales:
        item_profit = (sale.price_per_unit - sale.purchase_rate_at_sale) * sale.quantity
        if item_profit >= 0:
            profit_total += item_profit
        else:
            loss_total += abs(item_profit)
    
    # Fetch expenses
    daily_expenses = db.query(models.DailyExpense).filter(*expense_filter).all()
    one_time_expenses = db.query(models.OneTimeExpense).filter(*one_time_expense_filter).all()
    total_expenses = sum(e.amount for e in daily_expenses) + sum(e.amount for e in one_time_expenses)
    
    # Fetch investments
    investments = db.query(models.Investment).filter(*investment_filter).all()
    total_investments = sum(i.amount for i in investments)
    
    # Calculate liquidity (cash, upi) and credit
    cash_balance = 0.0
    upi_balance = 0.0
    credit_due = 0.0
    credit_recovered = 0.0
    
    for sale in regular_sales:
        amount = sale.total_amount
        if sale.payment_method == "Cash":
            cash_balance += amount
        elif sale.payment_method == "UPI":
            upi_balance += amount
        elif sale.payment_method == "Credit":
            credit_due += amount
    
    # Add investment amounts
    for inv in investments:
        if inv.payment_method == "Cash":
            cash_balance += inv.amount
        elif inv.payment_method == "UPI":
            upi_balance += inv.amount
    
    # Subtract expenses
    for exp in daily_expenses:
        if exp.payment_method == "Cash":
            cash_balance -= exp.amount
        elif exp.payment_method == "UPI":
            upi_balance -= exp.amount
    
    for exp in one_time_expenses:
        if exp.payment_method == "Cash":
            cash_balance -= exp.amount
        elif exp.payment_method == "UPI":
            upi_balance -= exp.amount
    
    return schemas.SummaryOut(
        sales=sales_total,
        net_sales=net_sales,
        profit=profit_total,
        loss=loss_total,
        inventory_value=inventory_value,
        cash_balance=cash_balance,
        upi_balance=upi_balance,
        credit_due=credit_due,
        expenses=total_expenses,
        investments=total_investments,
        returns=returns_total,
        credit_recovered=credit_recovered
    )

@router.get("/", response_model=schemas.SummaryOut)
def get_summary(
    period: str = Query("daily", pattern="^(daily|monthly|yearly|lifetime)$"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return calculate_summary(current_user, db, period)
