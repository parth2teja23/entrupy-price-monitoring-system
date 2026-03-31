from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.session import get_db
from models.product import Product
from schemas.product import ProductInDB, ProductCreate, ProductUpdate
from services.notifier import notify_price_change

router = APIRouter()

@router.post("/", response_model=ProductInDB, status_code=201)
async def create_product(product_in: ProductCreate, db: AsyncSession = Depends(get_db)):
    # Check if a product with the same product_url already exists
    result = await db.execute(select(Product).where(Product.product_url == product_in.product_url))
    db_product = result.scalar_one_or_none()
    
    if db_product:
        raise HTTPException(
            status_code=409, 
            detail="A product with this product_url already exists."
        )

    # Proceed with creation
    new_product = Product(**product_in.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    return new_product

@router.get("/{product_id}", response_model=ProductInDB)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    return db_product

@router.get("/", response_model=List[ProductInDB])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    source: str | None = None,
    brand: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Product)
    
    # Optional filters
    if source:
        stmt = stmt.where(Product.source == source)
    if brand:
        stmt = stmt.where(Product.brand == brand)
        
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    products = result.scalars().all()
    
    return products

@router.put("/{product_id}", response_model=ProductInDB)
async def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    old_price = db_product.price
    
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    
    # Trigger background notification if the price actually changed
    if product_update.price is not None and product_update.price != old_price:
        background_tasks.add_task(
            notify_price_change, 
            product_id=db_product.id,
            product_name=db_product.model,
            old_price=old_price,
            new_price=db_product.price
        )
    
    return db_product

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    await db.delete(db_product)
    await db.commit()
    return None