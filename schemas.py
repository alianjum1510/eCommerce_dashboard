from pydantic import BaseModel
from typing import Optional, List,Union
from datetime import datetime, date

class RevenueStat(BaseModel):
    period: Union[str, date]
    total_revenue: float
    total_units_sold: int

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    brand: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class InventoryBase(BaseModel):
    product_id: int
    quantity: int

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: int

class InventoryResponse(InventoryBase):
    id: int
    last_updated: datetime
    product: ProductResponse

    class Config:
        orm_mode = True


class SaleBase(BaseModel):
    product_id: int
    quantity_sold: int
    unit_price: float
    platform: str

class SaleResponse(SaleBase):
    id: int
    sale_date: date
    product: ProductResponse

    class Config:
        orm_mode = True




