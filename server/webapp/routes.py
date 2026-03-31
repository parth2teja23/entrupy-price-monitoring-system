from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta, timezone

from app.database import get_db
from models.product import Product
from models.history import PriceChangeEvent, PriceHistory

# To decouple templates, we mount it directly from the top level
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter(include_in_schema=False)

@router.get("/")
async def dashboard_page(request: Request, db: AsyncSession = Depends(get_db)):
    # Calculate some dashboard stats directly or call internal service
    source_stats_query = select(Product.source, func.count(Product.id)).group_by(Product.source)
    res_source = await db.execute(source_stats_query)
    by_source = {row[0]: row[1] for row in res_source.all()}
    
    cat_stats_query = select(Product.category, func.count(Product.id)).group_by(Product.category)
    res_cat = await db.execute(cat_stats_query)
    by_category = {row[0]: row[1] for row in res_cat.all()}
    
    total_products = sum(by_source.values())
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_products": total_products,
        "by_source": by_source,
        "by_category": by_category
    })

@router.get("/products")
async def products_list_page(
    request: Request, 
    page: int = 1, 
    limit: int = 50,
    source: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).order_by(Product.name)
    if source:
        query = query.where(Product.source == source)
        
    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    
    res = await db.execute(paginated_query)
    products = res.scalars().all()
    
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
        "page": page,
        "limit": limit,
        "source_filter": source
    })

@router.get("/products/{product_id}")
async def product_detail_page(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    product = res.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    hist_res = await db.execute(
        select(PriceHistory).where(PriceHistory.product_id == product_id).order_by(PriceHistory.timestamp)
    )
    history = hist_res.scalars().all()
    
    # Prepare chart data
    labels = [h.timestamp.strftime("%Y-%m-%d %H:%M") for h in history]
    prices = [h.price for h in history]
    
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "chart_labels": labels,
        "chart_prices": prices,
        "history": history
    })
