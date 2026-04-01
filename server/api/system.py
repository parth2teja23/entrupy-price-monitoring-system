from __future__ import annotations
from __future__ import annotations
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import os
import aiofiles

from db.session import get_db
from models.product import Product
from services.price_tracker import PriceTrackerService
from api.deps import verify_api_key
from scrapers import FirstDibsScraper, FashionphileScraper, GrailedScraper

router = APIRouter(prefix="/system", tags=["System"])

@router.post("/refresh")
async def trigger_refresh(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    tracker = PriceTrackerService(db)
    
    # Path to sample products
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(project_root, "sample_products")
    
    scrapers = [
        FirstDibsScraper(data_dir),
        FashionphileScraper(data_dir),
        GrailedScraper(data_dir)
    ]
    
    async def process_scraper(scraper, trk):
        count = 0
        async for product in scraper.fetch_listings():
            await trk.process_scraped_product(product)
            count += 1
        return count

    import asyncio
    # Run all scrapers concurrently just like you described!
    tasks = [process_scraper(s, tracker) for s in scrapers]
    results = await asyncio.gather(*tasks)
    total_processed = sum(results)
            
    await db.commit()
    
    return {"status": "success", "message": "Scrape refresh completed", "total_processed": total_processed}
