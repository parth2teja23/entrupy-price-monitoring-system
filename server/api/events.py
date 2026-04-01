from __future__ import annotations
from __future__ import annotations
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl

from db.session import get_db
from models.history import PriceChangeEvent
from api.deps import verify_api_key

router = APIRouter(prefix="/events", tags=["Events"])

class EventResponse(BaseModel):
    id: int
    product_id: int
    old_price: Optional[float]
    new_price: float
    percentage_change: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedEvents(BaseModel):
    total: int
    page: int
    limit: int
    items: List[EventResponse]

@router.get("/", response_model=PaginatedEvents)
async def get_events(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    product_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    query = select(PriceChangeEvent)
    
    if product_id:
        query = query.where(PriceChangeEvent.product_id == product_id)
        
    query = query.order_by(PriceChangeEvent.created_at.desc())
    
    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    
    result = await db.execute(paginated_query)
    items = result.scalars().all()
    
    # Needs count logic
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items
    }
