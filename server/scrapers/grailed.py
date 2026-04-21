from __future__ import annotations
from __future__ import annotations
import logging
from typing import AsyncGenerator

import httpx

from .base import BaseScraper
from .models import ScrapedProduct

logger = logging.getLogger(__name__)

class GrailedScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "grailed"

    @property
    def endpoint_path(self) -> str:
        return "/internal/marketplaces/grailed"

    async def fetch_listings(self, client: httpx.AsyncClient, simulate: bool = False) -> AsyncGenerator[ScrapedProduct, None]:
        try:
            payload = await self.fetch_json(client, simulate=simulate)
        except Exception as exc:
            logger.error(f"Failed to fetch grailed listings: {exc}")
            return

        for data in payload:
            url = data.get("product_url", "")
            external_id = data.get("product_id") or (url.split("/")[-1] if url else url)

            yield ScrapedProduct(
                external_id=str(external_id),
                source="grailed",
                title=data.get("model", "Unknown"),
                price=float(data.get("price", 0)),
                currency="USD",
                url=url,
                category=data.get("category", "apparel"),
                condition=data.get("condition", "Unknown"),
                image_url=(data.get("main_images") or [{}])[0].get("url") if data.get("main_images") else None,
            )
