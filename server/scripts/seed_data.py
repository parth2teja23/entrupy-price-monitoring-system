import asyncio
import json
import os
import sys

# Add server directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.session import AsyncSessionLocal
from models.product import Product

# Modified to locate the `sample_products` directory accurately
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "sample_products")

def guess_source_from_filename(filename: str) -> str:
    """Extract source identifier from the filename (e.g., '1stdibs', 'fashionphile', 'grailed')."""
    if "1stdibs" in filename:
        return "1stdibs"
    if "fashionphile" in filename:
        return "fashionphile"
    if "grailed" in filename:
        return "grailed"
    return "unknown"

async def import_products():
    if not os.path.exists(SAMPLE_DIR):
        print(f"Error: Sample directory not found at {SAMPLE_DIR}")
        return

    json_files = [f for f in os.listdir(SAMPLE_DIR) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files to process.")

    imported_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as db:
        for filename in json_files:
            file_path = os.path.join(SAMPLE_DIR, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse {filename}: {e}")
                    continue

                source_name = guess_source_from_filename(filename)
                product_url = data.get("product_url")
                
                if not product_url:
                    print(f"Skipping {filename} - missing product_url")
                    continue

                # Clean price: remove non-numeric chars if it's stored as a string (e.g. "$1,200.00")
                raw_price = data.get("price", 0)
                price_float = 0.0
                if isinstance(raw_price, (int, float)):
                    price_float = float(raw_price)
                elif isinstance(raw_price, str):
                    clean_str = ''.join(c for c in raw_price if c.isdigit() or c == '.')
                    if clean_str:
                        price_float = float(clean_str)

                # Check if product already exists
                result = await db.execute(select(Product).where(Product.product_url == product_url))
                existing_product = result.scalar_one_or_none()

                if existing_product:
                    # Optional: update logic here, but for seeding we usually skip duplicates
                    skipped_count += 1
                    continue

                new_product = Product(
                    source=source_name,
                    brand=data.get("brand", "Unknown"),
                    model=data.get("model", "Unknown Model"),
                    price=price_float,
                    size=data.get("size"),
                    full_description=data.get("full_description"),
                    product_url=product_url,
                    main_images=data.get("main_images", [])
                )
                
                db.add(new_product)
                imported_count += 1

        print("Committing to database...")
        await db.commit()
    
    print(f"Import complete! Imported: {imported_count}, Skipped (Duplicates): {skipped_count}")

if __name__ == "__main__":
    asyncio.run(import_products())