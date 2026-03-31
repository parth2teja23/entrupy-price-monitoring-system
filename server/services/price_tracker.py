import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.product import Product
from models.history import PriceHistory, PriceChangeEvent
from scrapers.models import ScrapedProduct

logger = logging.getLogger(__name__)

class PriceTrackerService:
    """Manages the business logic of upserting products and tracking price variations over time."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_scraped_product(self, item: ScrapedProduct) -> Product:
        """
        Takes a raw scraper result, maps it into the database, updates the current price,
        and logs to the price_history and price_change_events ledger if the price shifted.
        """
        # 1. Look up existing product by its unique composite identifier
        result = await self.db.execute(
            select(Product).where(
                Product.external_id == item.external_id,
                Product.source == item.source
            )
        )
        existing_product = result.scalar_one_or_none()

        price_changed = False
        old_price = 0.0

        if existing_product:
            # Check if price shifted
            if abs(existing_product.price - item.price) > 0.01:
                price_changed = True
                old_price = existing_product.price
            
            # Update mutable fields (UPSERT pattern logic)
            existing_product.title = item.title
            existing_product.price = item.price
            existing_product.is_sold = item.is_sold
            existing_product.last_seen_at = datetime.now(timezone.utc)
            # You can update more fields here if needed

            product_record = existing_product
        else:
            # Insert brand new product
            product_record = Product(
                external_id=item.external_id,
                source=item.source,
                title=item.title,
                brand=item.brand,
                category=item.category,
                condition=item.condition,
                price=item.price,
                currency=item.currency,
                url=item.url,
                image_url=item.image_url,
                is_sold=item.is_sold
            )
            self.db.add(product_record)
            
            # Always log initial price into history table
            price_changed = True
            old_price = item.price  # First time, so old effectively equals new for PCT calculation handling

        # Flush to DB early to get an active ID for tracking relations
        await self.db.flush() 

        # 2. Append ledger if Price changed (or is brand new)
        if price_changed:
            history_record = PriceHistory(
                product_id=product_record.id,
                price=item.price
            )
            self.db.add(history_record)

            # 3. Generate webhook notification events ONLY if it's an existing item that shifted price
            if existing_product and old_price != item.price:
                change_pct = ((item.price - old_price) / old_price) * 100.0 if old_price > 0 else 0
                
                event_record = PriceChangeEvent(
                    product_id=product_record.id,
                    old_price=old_price,
                    new_price=item.price,
                    change_pct=change_pct,
                    delivered=False
                )
                self.db.add(event_record)
                logger.info(f"Price change detected for {item.title}: {old_price} -> {item.price}")
        
        return product_record