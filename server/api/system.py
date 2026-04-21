from __future__ import annotations
from __future__ import annotations
import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient, ASGITransport

from db.session import get_db
from services.price_tracker import PriceTrackerService
from api.deps import verify_api_key
from scrapers import FirstDibsScraper, FashionphileScraper, GrailedScraper

router = APIRouter(prefix="/system", tags=["System"])

@router.post("/refresh")
async def trigger_refresh(
    background_tasks: BackgroundTasks,
    request: Request,
    simulate: bool = False,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    scrapers = [
        FirstDibsScraper(),
        FashionphileScraper(),
        GrailedScraper()
    ]

    async def collect_scraper(scraper):
        items = []
        async with AsyncClient(
            transport=ASGITransport(app=request.app),
            base_url="http://testserver"
        ) as client:
            async for product in scraper.fetch_listings(client, simulate=simulate):
                items.append(product)
        return items

    batches = await asyncio.gather(*(collect_scraper(scraper) for scraper in scrapers))

    tracker = PriceTrackerService(db)
    total_processed = 0
    for batch in batches:
        for product in batch:
            await tracker.process_scraped_product(product)
            total_processed += 1

    await db.commit()
    
    return {"status": "success", "message": "Scrape refresh completed", "total_processed": total_processed}
