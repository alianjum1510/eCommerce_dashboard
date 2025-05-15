from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database import Base, SessionLocal
from models import Product, Inventory, Sale, Category, ProductCategory, InventoryLog
from datetime import date, timedelta, datetime
import random

def populate_demo_data(db: Session):
    categories = ["Electronics", "Home & Kitchen", "Books", "Toys", "Fashion"]
    category_objs = []
    for name in categories:
        cat = Category(name=name)
        db.add(cat)
        category_objs.append(cat)
    db.flush()

    products_data = [
        {"name": "Wireless Mouse", "category": "Electronics", "price": 25.99, "brand": "LogiTech"},
        {"name": "Noise Cancelling Headphones", "category": "Electronics", "price": 89.99, "brand": "Sony"},
        {"name": "Blender", "category": "Home & Kitchen", "price": 45.50, "brand": "Philips"},
        {"name": "Novel - Sci-Fi", "category": "Books", "price": 12.99, "brand": "Penguin"},
        {"name": "Lego Building Set", "category": "Toys", "price": 34.95, "brand": "LEGO"},
        {"name": "Men’s T-shirt", "category": "Fashion", "price": 15.00, "brand": "H&M"},
    ]

    product_objs = []
    for product in products_data:
        prod = Product(
            name=product["name"],
            category=product["category"],
            price=product["price"],
            brand=product["brand"]
        )
        db.add(prod)
        product_objs.append(prod)
    db.flush()

    for prod in product_objs:
        matched_category = next((c for c in category_objs if c.name == prod.category), None)
        if matched_category:
            link = ProductCategory(product_id=prod.id, category_id=matched_category.id)
            db.add(link)

    for prod in product_objs:
        quantity = random.randint(10, 300)
        inv = Inventory(product_id=prod.id, quantity=quantity)
        db.add(inv)
        db.flush()

        log = InventoryLog(
            product_id=prod.id,
            quantity_before=0,
            quantity_after=quantity,
            timestamp=datetime.utcnow()
        )
        db.add(log)

    platforms = ["Amazon", "Walmart"]
    for prod in product_objs:
        for days_ago in range(1, 30):
            sale = Sale(
                product_id=prod.id,
                quantity_sold=random.randint(1, 10),
                unit_price=prod.price,
                sale_date=date.today() - timedelta(days=days_ago),
                platform=random.choice(platforms)
            )
            db.add(sale)

    db.commit()
    print("Demo data populated successfully.")


if __name__ == "__main__":
   
    Base.metadata.create_all(bind=create_engine("postgresql://postgres:"))

    db = SessionLocal()
    try:
        populate_demo_data(db)
    finally:
        db.close()
