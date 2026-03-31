from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta, timezone

from app.database import get_db
from models.product import Product
from models.history import PriceChangeEvent
from api.deps import get_current_api_key

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    # Total products grouped by source
    source_stats_query = select(Product.source, func.count(Product.id)).group_by(Product.source)
    source_stats_result = await db.execute(source_stats_query)
    by_source = {row[0]: row[1] for row in source_stats_result.all()}
    
    # Products grouped by category
    category_stats_query = select(Product.category, func.count(Product.id)).group_by(Product.category)
    category_stats_result = await db.execute(category_stats_query)
    by_category = {row[0]: row[1] for row in category_stats_result.all()}
    
    # Count of price changes in last 24h
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    
    changes_query = select(func.count(PriceChangeEvent.id)).where(PriceChangeEvent.created_at >= yesterday)
    changes_result = await db.execute(changes_query)
    changes_24h = changes_result.scalar() or 0
    
    return {
        "total_products": sum(by_source.values()),
        "by_source": by_source,
        "by_category": by_category,
        "price_changes_24h": changes_24h
    }
