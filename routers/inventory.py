from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models import Product, Inventory,InventoryLog
from schemas import InventoryUpdate, InventoryResponse
from database import SessionLocal, get_db
import datetime
from datetime import datetime

router = APIRouter()


@router.get("/inventory/", response_model=List[InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    inventory_items = db.query(Inventory).join(Product).all()
    if not inventory_items:
        raise HTTPException(status_code=200, detail="No inventory found")
    return inventory_items


@router.get("/inventory/low-stock/", response_model=List[InventoryResponse])
def get_low_stock(db: Session = Depends(get_db), threshold: int = 10):
    low_stock_items = db.query(Inventory).join(Product).filter(Inventory.quantity < threshold).all()
    if not low_stock_items:
        raise HTTPException(status_code=200, detail="No low stock items found")
    return low_stock_items


@router.put("/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int, inventory_update: InventoryUpdate, db: Session = Depends(get_db)):

    inventory_item = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory_item:
        raise HTTPException(status_code=200, detail="Inventory not found for this product")

    quantity_before = inventory_item.quantity
    inventory_item.quantity = inventory_update.quantity
    inventory_item.last_updated = datetime.utcnow()
    log_entry = InventoryLog(
        product_id=product_id,
        quantity_before=quantity_before,
        quantity_after=inventory_update.quantity,
    )
    db.add(log_entry)
    db.commit()

    return inventory_item


@router.get("/inventory/logs/{product_id}")
def get_inventory_logs(product_id: int, db: Session = Depends(get_db)):
    logs = db.query(InventoryLog).filter(InventoryLog.product_id == product_id).order_by(InventoryLog.timestamp.desc()).all()
    if not logs:
        raise HTTPException(status_code=400, detail="No logs found for this product")
    return logs
