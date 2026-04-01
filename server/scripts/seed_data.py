from __future__ import annotations
from __future__ import annotations
import asyncio
import json
import os
import sys

# Add server directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import AsyncSessionLocal
from scrapers.models import ScrapedProduct
from services.price_tracker import PriceTrackerService

# Modified to locate the `sample_products` directory accurately
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "sample_products")

def guess_source_from_filename(filename: str) -> str:
    """Extract source identifier from the filename."""
    if "1stdibs" in filename: return "1stdibs"
    if "fashionphile" in filename: return "fashionphile"
    if "grailed" in filename: return "grailed"
    return "unknown"

async def mock_scraper_generator():
    """Simulates a Data Scraper reading all existing files dynamically"""
    if not os.path.exists(SAMPLE_DIR):
        print(f"Error: Sample directory not found at {SAMPLE_DIR}")
        return

    json_files = [f for f in os.listdir(SAMPLE_DIR) if f.endswith('.json')]
    print(f"Loading {len(json_files)} simulated scraper targets.")

    for filename in json_files:
        file_path = os.path.join(SAMPLE_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

            source_name = guess_source_from_filename(filename)
            product_url = data.get("product_url", "")
            
            # Map external_id. If missing in sample data, hash the URL uniquely.
            external_id = data.get("id") or str(hash(product_url))

            # Clean price string explicitly into floats
            raw_price = data.get("price", 0)
            price_float = 0.0
            if isinstance(raw_price, (int, float)):
                price_float = float(raw_price)
            elif isinstance(raw_price, str):
                clean_str = ''.join(c for c in raw_price if c.isdigit() or c == '.')
                if clean_str: price_float = float(clean_str)

            # Map image URL (first element string mapping)
            main_images = data.get("main_images", [])
            image_url = main_images[0].get("url") if main_images and isinstance(main_images[0], dict) else None

            yield ScrapedProduct(
                external_id=external_id,
                source=source_name,
                title=data.get("model", "Unknown Item"),
                brand=data.get("brand", "Unknown"),
                price=price_float,
                url=product_url,
                image_url=image_url,
                category=data.get("category", "General"),
                condition=data.get("condition", "Used")
            )

async def import_products():
    imported_count = 0
    async with AsyncSessionLocal() as db:
        tracker = PriceTrackerService(db)
        
        async for item in mock_scraper_generator():
            await tracker.process_scraped_product(item)
            imported_count += 1
            
        print("Committing transaction batch...")
        await db.commit()
    
    print(f"Scraper Data Seeding Complete! Simulated and imported {imported_count} listings across all sources.")

if __name__ == "__main__":
    asyncio.run(import_products())