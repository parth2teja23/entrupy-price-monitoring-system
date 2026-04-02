from __future__ import annotations
from __future__ import annotations
from api.deps import verify_api_key
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.session import get_db
from models.product import Product
from models.history import PriceHistory
from schemas.product import ProductOut, ProductDetailOut, PaginatedProducts

router = APIRouter(prefix="/products", tags=["Products"])

@router.get(
    "/",
    response_model=PaginatedProducts,
    summary="List products with filters",
    description="Retrieve a paginated list of tracking products, allowing filtering by source, category, and minimum or maximum prices."
)
async def list_products(
    api_key: str = Depends(verify_api_key),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Category filter"),
    source: str | None = Query(None, description="Marketplace source"),
    min_price: float | None = Query(None, description="Minimum price filter"),
    max_price: float | None = Query(None, description="Maximum price filter"),
    db: AsyncSession = Depends(get_db)
):
    if min_price and max_price and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")

    stmt = select(Product)
    
    if category:
        stmt = stmt.where(Product.category == category)
    if source:
        stmt = stmt.where(Product.source == source)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    # Calculate Total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # Fetch Page Limits
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return {"total": total or 0, "page": page, "limit": limit, "items": items}

@router.get(
    "/{id}",
    response_model=ProductDetailOut,
    summary="Get product details",
    description="Fetch a single product along with a snapshot of its immediate price history."
)
async def get_product(
    id: int,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Fetch price history array mapping alongside the detail view
    hist_result = await db.execute(
        select(PriceHistory).where(PriceHistory.product_id == id).order_by(PriceHistory.recorded_at.desc())
    )
    history = hist_result.scalars().all()
    
    out = ProductDetailOut.model_validate(product)
    out.price_history = history
    return out
from schemas.product import PaginatedPriceHistory
from datetime import datetime

@router.get(
    "/{id}/history",
    response_model=PaginatedPriceHistory,
    summary="Get product price history",
    description="Retrieve a paginated historical ledger of all prices recorded for a specific product."
)
async def get_product_history(
    id: int,
    api_key: str = Depends(verify_api_key),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Items per page"),
    since: datetime | None = Query(None, description="Only fetch history after this date"),
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = select(PriceHistory).where(PriceHistory.product_id == id)
    if since:
        stmt = stmt.where(PriceHistory.recorded_at >= since)
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(PriceHistory.recorded_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    history = result.scalars().all()

    return {"total": total or 0, "page": page, "limit": limit, "items": history}
