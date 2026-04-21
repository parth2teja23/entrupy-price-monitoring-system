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

    model_config = {"from_attributes": True}

class PaginatedEvents(BaseModel):
    total: int
    page: int
    limit: int
    items: List[EventResponse]

@router.get(
    "/",
    response_model=PaginatedEvents,
    summary="List price change events",
    description="Fetch a paginated list of all system price change events, optionally filtered by product or delivery status."
)
async def get_events(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=500, description="Items per page"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    delivered: Optional[bool] = Query(None, description="Filter undelivered polling events"),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    query = select(PriceChangeEvent)

    if product_id:
        query = query.where(PriceChangeEvent.product_id == product_id)
        
    if delivered is not None:
        query = query.where(PriceChangeEvent.delivered == delivered)
        
    query = query.order_by(PriceChangeEvent.created_at.desc())
    
    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    
    result = await db.execute(paginated_query)
    db_items = result.scalars().all()
    items = [
        EventResponse(
            id=item.id,
            product_id=item.product_id,
            old_price=item.old_price,
            new_price=item.new_price,
            percentage_change=item.change_pct,
            created_at=item.created_at,
        )
        for item in db_items
    ]
    
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
