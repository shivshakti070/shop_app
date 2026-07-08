from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class InventoryBase(BaseModel):
    date: str
    item: str
    brand: str
    initial_quantity: int
    purchase_rate: float

class InventoryCreate(InventoryBase):
    pass

class InventoryOut(InventoryBase):
    id: int
    remaining_quantity: int
    owner_id: int

    class Config:
        from_attributes = True

class DailySaleBase(BaseModel):
    date: str

    inventory_item_id: int

    item_name: str

    brand: str

    quantity: int

    price_per_unit: float

    total_amount: float

    purchase_rate_at_sale: float = 0.0

    payment_method: str = "Cash"

    customer_name: Optional[str] = None


class DailySaleCreate(DailySaleBase):
    pass


class DailySaleOut(BaseModel):
    id: int
    date: str
    inventory_item_id: int
    item_name: str
    brand: str
    quantity: int
    price_per_unit: float
    total_amount: float
    purchase_rate_at_sale: float
    payment_method: str
    customer_name: Optional[str]
    is_return: bool = False

    class Config:
        from_attributes = True


class SalesReturnCreate(BaseModel):
    date: str
    sale_id: int
    quantity: int
    refund_amount: float
    reason: Optional[str] = None


class SalesReturnOut(SalesReturnCreate):
    id: int
    inventory_id: int
    owner_id: int

    class Config:
        from_attributes = True


class DailyExpenseBase(BaseModel):
    date: str
    description: str
    amount: float
    category: str
    payment_method: str = "Cash"

class DailyExpenseCreate(DailyExpenseBase):
    pass

class DailyExpenseOut(DailyExpenseBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class InvestmentBase(BaseModel):
    date: str
    source: str
    amount: float
    notes: str
    payment_method: str = "Cash"

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentOut(InvestmentBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class SummaryOut(BaseModel):
    sales: float
    net_sales: float
    profit: float
    loss: float
    inventory_value: float
    cash_balance: float
    upi_balance: float
    credit_due: float
    expenses: float
    investments: float
    returns: float
    credit_recovered: float

class OneTimeExpenseBase(BaseModel):
    date: str
    description: str
    amount: float
    category: str
    payment_method: str = "Cash"

class OneTimeExpenseCreate(OneTimeExpenseBase):
    pass

class OneTimeExpenseOut(OneTimeExpenseBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
