from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("InventoryItem", back_populates="owner")
    sales = relationship("DailySale", back_populates="owner")
    expenses = relationship("DailyExpense", back_populates="owner")
    investments = relationship("Investment", back_populates="owner")
    one_time_expenses = relationship("OneTimeExpense", back_populates="owner")


class OneTimeExpense(Base):
    __tablename__ = "one_time_expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    description = Column(String)
    amount = Column(Float, default=0.0)
    category = Column(String)
    payment_method = Column(String, default="Cash")
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="one_time_expenses")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(String, index=True)

    item = Column(String, index=True)

    brand = Column(String, index=True)

    initial_quantity = Column(Integer, default=0)

    remaining_quantity = Column(Integer, default=0)

    purchase_rate = Column(Float, default=0.0)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

    sales = relationship("DailySale", back_populates="inventory_item")


class DailySale(Base):
    __tablename__ = "daily_sales"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(String, index=True)

    inventory_item_id = Column(
        Integer,
        ForeignKey("inventory_items.id"),
        nullable=False
    )

    item_name = Column(String)

    brand = Column(String)

    quantity = Column(Integer, default=0)

    price_per_unit = Column(Float, default=0.0)

    total_amount = Column(Float, default=0.0)

    purchase_rate_at_sale = Column(Float, default=0.0)

    payment_method = Column(String, default="Cash")

    customer_name = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="sales")

    inventory_item = relationship("InventoryItem", back_populates="sales")


class DailyExpense(Base):
    __tablename__ = "daily_expenses"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(String, index=True)

    description = Column(String, index=True)

    amount = Column(Float, default=0.0)

    category = Column(String, index=True)

    payment_method = Column(String, default="Cash")

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="expenses")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(String, index=True)

    source = Column(String, index=True)

    amount = Column(Float, default=0.0)

    notes = Column(String, index=True)

    payment_method = Column(String, default="Cash")

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="investments")