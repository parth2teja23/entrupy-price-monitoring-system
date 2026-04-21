from __future__ import annotations
from __future__ import annotations
import asyncio
import json
import os
import sys
from pathlib import Path

# Add server directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import AsyncSessionLocal
from scrapers.models import ScrapedProduct
from services.price_tracker import PriceTrackerService
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Resolve the sample directory from the project root so seeding works
# regardless of whether the script is launched from server/ or the repo root.
SERVER_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SERVER_DIR.parent

SAMPLE_DIR_CANDIDATES = [
    SERVER_DIR / "sample_products",
    PROJECT_DIR / "sample_products",
    PROJECT_DIR.parent / "sample_products",
]

SAMPLE_DIR = next((path for path in SAMPLE_DIR_CANDIDATES if path.exists()), SAMPLE_DIR_CANDIDATES[0])

def guess_source_from_filename(filename: str) -> str:
    """Extract source identifier from the filename."""
    if "1stdibs" in filename: return "1stdibs"
    if "fashionphile" in filename: return "fashionphile"
    if "grailed" in filename: return "grailed"
    return "unknown"

async def mock_scraper_generator():
    """Simulates a Data Scraper reading all existing files dynamically."""
    if not SAMPLE_DIR.exists():
        logger.error(f"Sample directory not found at {SAMPLE_DIR}")
        return

    json_files = sorted(path for path in SAMPLE_DIR.iterdir() if path.suffix == ".json")
    logger.info(f"Loading {len(json_files)} simulated scraper targets from directory: {SAMPLE_DIR}")

    for file_path in json_files:
        with file_path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as err:
                logger.error(f"Failed to parse JSON file {file_path.name}: {err}")
                continue

            source_name = guess_source_from_filename(file_path.name)
            product_url = data.get("product_url", "")

            # Map external_id. If missing in sample data, hash the URL uniquely.
            external_id = data.get("product_id") or data.get("id") or str(hash(product_url))

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
                external_id=str(external_id),
                source=source_name,
                title=data.get("model", "Unknown Item"),
                brand=data.get("brand", "Unknown"),
                price=price_float,
                url=product_url,
                image_url=image_url,
                category=data.get("category", "General"),
                condition=data.get("condition", "Used"),
            )

async def import_products():
    imported_count = 0
    
    async with AsyncSessionLocal() as db:
        tracker = PriceTrackerService(db)

        async for item in mock_scraper_generator():
            await tracker.process_scraped_product(item)
            imported_count += 1
            
        logger.info("Committing transaction batch...")
        await db.commit()

    logger.info(f"Scraper Data Seeding Complete! Simulated and imported {imported_count} listings across all sources.")

if __name__ == "__main__":
    asyncio.run(import_products())