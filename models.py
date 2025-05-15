from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, date


# -------------------- Product Table --------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    brand = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inventory = relationship("Inventory", back_populates="product", uselist=False)
    sales = relationship("Sale", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")
    product_categories = relationship("ProductCategory", back_populates="product")


# -------------------- Inventory Table --------------------
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory")


# -------------------- Inventory Log Table --------------------
class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_logs")


# -------------------- Sales Table --------------------
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # snapshot of price at time of sale
    sale_date = Column(Date, default=date.today)
    platform = Column(String, nullable=False)  # e.g., "Amazon", "Walmart"

    product = relationship("Product", back_populates="sales")


# -------------------- Category Table --------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    products = relationship("ProductCategory", back_populates="category")


# -------------------- Product-Category Association Table --------------------
class ProductCategory(Base):
    __tablename__ = "product_categories"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)

    product = relationship("Product", back_populates="product_categories")
    category = relationship("Category", back_populates="products")
