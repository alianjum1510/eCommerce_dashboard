from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract,desc, cast, String,text
from typing import List, Optional
from datetime import date
from database import SessionLocal,get_db
from models import Sale, Product
from schemas import SaleResponse, RevenueStat
from sqlalchemy.sql import label
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case


router = APIRouter()


@router.get("/sales", response_model=List[SaleResponse])
def get_all_sales(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Filter sales from this date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter sales up to this date (YYYY-MM-DD)"),
    platform: Optional[str] = Query(None, description="Filter sales by platform (Amazon, Flipkart)"),
):
    try:
        query = db.query(Sale)

        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
        if platform:
            query = query.filter(Sale.platform == platform)

        results = query.order_by(Sale.sale_date.desc()).all()
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/sales/summary/")
def sales_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] =  Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[date] =  Query(None, description="End date for filtering (YYYY-MM-DD)"),
):
    try:
        query = db.query(Sale)

        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)

        sales = query.all()

        total_quantity = sum(s.quantity_sold for s in sales)
        total_revenue = sum(s.quantity_sold * s.unit_price for s in sales)

        return {
            "total_sales": len(sales),
            "total_quantity_sold": total_quantity,
            "total_revenue": total_revenue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


@router.get("/sales/revenue/daily", response_model=List[RevenueStat])
def get_daily_revenue(db: Session = Depends(get_db)):
    try:    
        results = (
            db.query(
                Sale.sale_date.label("period"),
                func.sum(Sale.unit_price * Sale.quantity_sold).label("total_revenue"),
                func.sum(Sale.quantity_sold).label("total_units_sold")
            )
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date.desc())
            .all()
        )
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


@router.get("/sales/revenue/weekly", response_model=List[RevenueStat])
def get_weekly_revenue(db: Session = Depends(get_db)):
    try:
        period_label = label(
            "period",
            func.concat(
                func.extract('year', Sale.sale_date),
                '-W',
                func.lpad(cast(func.extract('week', Sale.sale_date), String), 2, '0')  # Format week like '04', '11'
            )
        )

        results = (
            db.query(
                period_label,
                func.sum(Sale.unit_price * Sale.quantity_sold).label("total_revenue"),
                func.sum(Sale.quantity_sold).label("total_units_sold")
            )
            .group_by(period_label)
            .order_by(desc(period_label)) 
            .all()
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


@router.get("/sales/revenue/monthly", response_model=List[RevenueStat])
def get_monthly_revenue(db: Session = Depends(get_db)):
    try:
        period_label = func.to_char(Sale.sale_date, 'YYYY-MM').label("period")

        results = (
            db.query(
                period_label,
                func.sum(Sale.unit_price * Sale.quantity_sold).label("total_revenue"),
                func.sum(Sale.quantity_sold).label("total_units_sold")
            )
            .group_by(period_label)
            .order_by(desc(period_label))  # Use label directly
            .all()
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


@router.get("/sales/revenue/annual", response_model=List[RevenueStat])
def get_annual_revenue(db: Session = Depends(get_db)):
    try:
        period_label = func.to_char(Sale.sale_date, 'YYYY').label("period")

        results = (
            db.query(
                period_label,
                func.sum(Sale.unit_price * Sale.quantity_sold).label("total_revenue"),
                func.sum(Sale.quantity_sold).label("total_units_sold")
            )
            .group_by(period_label)
            .order_by(desc(period_label))
            .all()
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


@router.get("/sales/revenue/comparison", response_model=List[RevenueStat])
def compare_revenue(
    db: Session = Depends(get_db),
    group_by: str = Query("month", enum=["day", "week", "month", "year"]),
    platform: Optional[str] = Query(None, description="Enter the platform Name(Amazon, Walmart)"),
    product_id: Optional[int] = Query(None, description="Enter the product ID"),
    start_date: Optional[date] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
):
    try:
        query = db.query(
            Sale.sale_date,
            Sale.unit_price,
            Sale.quantity_sold
        )

        if platform:
            query = query.filter(Sale.platform == platform)
        if product_id:
            query = query.filter(Sale.product_id == product_id)
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)

        if group_by == "day":
            period_label = Sale.sale_date.label("period")
        elif group_by == "week":
            period_label = func.concat(
                func.extract('year', Sale.sale_date),
                '-W',
                func.lpad(cast(func.extract('week', Sale.sale_date), String), 2, '0')
            ).label("period")
        elif group_by == "month":
            period_label = func.to_char(Sale.sale_date, 'YYYY-MM').label("period")
        elif group_by == "year":
            period_label = func.to_char(Sale.sale_date, 'YYYY').label("period")
        else:
            raise HTTPException(status_code=400, detail="Invalid group_by value")

        results = (
            db.query(
                period_label,
                func.sum(Sale.unit_price * Sale.quantity_sold).label("total_revenue"),
                func.sum(Sale.quantity_sold).label("total_units_sold")
            )
            .group_by(period_label)
            .order_by(desc(period_label))
            .all()
        ) 

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


@router.get("/sales/revenue/", response_model=List[RevenueStat])
def compare_revenue_by_product_and_category(
    db: Session = Depends(get_db),
    platform: Optional[str] = Query(None, description="Enter the platform Name(Amazon, Walmart)"),
    product_id: Optional[int] = Query(None, description="Enter the product ID"),
    category: Optional[str] = Query(None, description="Enter the category name"),
):
    try:
        query = db.query(
            Product.name.label("product_name"),
            Product.category.label("category_name"),
            func.sum(Sale.unit_price * Sale.quantity_sold).label("total_revenue"),
            func.sum(Sale.quantity_sold).label("total_units_sold")
        ).join(Product, Product.id == Sale.product_id)

        if platform:
            query = query.filter(Sale.platform == platform)
        if product_id:
            query = query.filter(Sale.product_id == product_id)
        if category:
            query = query.filter(Product.category == category)

        results = (
            query
            .group_by(Product.name, Product.category)
            .order_by(desc(func.sum(Sale.unit_price * Sale.quantity_sold)))
            .all()
        )

        formatted_results = [
            RevenueStat(
                period=f"Product: {r.product_name} | Category: {r.category_name}",
                total_revenue=r.total_revenue,
                total_units_sold=r.total_units_sold
            )
            for r in results
        ]

        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


