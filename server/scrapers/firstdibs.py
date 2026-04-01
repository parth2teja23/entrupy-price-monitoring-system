from __future__ import annotations
from __future__ import annotations
import json
import logging
from typing import AsyncGenerator
from pathlib import Path

from .base import BaseScraper
from .models import ScrapedProduct

logger = logging.getLogger(__name__)

class FirstDibsScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "1stdibs"

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    async def fetch_listings(self) -> AsyncGenerator[ScrapedProduct, None]:
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist.")
            return

        for file_path in self.data_dir.glob("1stdibs_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Process 1stdibs schema
                    url = data.get("product_url", "")
                    # Generate a unique stable ID from URL
                    external_id = url.split("/")[ -2 ] if "id-" in url else file_path.stem
                        
                    yield ScrapedProduct(
                        external_id=external_id,
                        source="1stdibs",
                        name=data.get("model", data.get("brand", "Unknown")),
                        price=float(data.get("price", 0)),
                        currency="USD", # Assuming USD for this sample
                        url=url,
                        category=data.get("category", "accessories"),
                        condition="Unknown"
                    )
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
