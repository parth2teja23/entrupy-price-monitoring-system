from __future__ import annotations
from __future__ import annotations
import json
import logging
from typing import AsyncGenerator
from pathlib import Path

from .base import BaseScraper
from .models import ScrapedProduct

logger = logging.getLogger(__name__)

class FashionphileScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "fashionphile"

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    async def fetch_listings(self) -> AsyncGenerator[ScrapedProduct, None]:
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist.")
            return

        for file_path in self.data_dir.glob("fashionphile_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Process fashionphile schema
                    url = data.get("product_url", "")
                    
                    # The external_id is usually the number at the end of the fashionphile url 1806623
                    url_parts = url.strip("/").split("-")
                    external_id = url_parts[-1] if url_parts else file_path.stem
                    
                    # Try extract name cleanly
                    name = " ".join(url.split("/")[-1].split("-")[:-1]).title()
                    
                    yield ScrapedProduct(
                        external_id=external_id,
                        source="fashionphile",
                        name=name or data.get("brand", "Unknown"),
                        price=float(data.get("price", 0)),
                        currency=data.get("currency", "USD"),
                        url=url,
                        category="jewelry",
                        condition=data.get("condition", "Unknown")
                    )
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
