from __future__ import annotations
from __future__ import annotations
import json
import logging
from typing import AsyncGenerator
from pathlib import Path

from .base import BaseScraper
from .models import ScrapedProduct

logger = logging.getLogger(__name__)

class GrailedScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "grailed"

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    async def fetch_listings(self) -> AsyncGenerator[ScrapedProduct, None]:
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist.")
            return

        for file_path in self.data_dir.glob("grailed_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    url = data.get("product_url", "")
                    
                    # For grailed: https://www.grailed.com/listings/83672676 -> 83672676
                    external_id = url.split("/")[-1] if url else file_path.stem
                    
                    yield ScrapedProduct(
                        external_id=external_id,
                        source="grailed",
                        name=data.get("model", "Unknown"),
                        price=float(data.get("price", 0)),
                        currency="USD", # Grailed default
                        url=url,
                        category="apparel",
                        condition="Unknown"
                    )
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
