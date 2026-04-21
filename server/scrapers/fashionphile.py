from __future__ import annotations
from __future__ import annotations
import logging
from typing import AsyncGenerator

import httpx

from .base import BaseScraper
from .models import ScrapedProduct

logger = logging.getLogger(__name__)

class FashionphileScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "fashionphile"

    @property
    def endpoint_path(self) -> str:
        return "/internal/marketplaces/fashionphile"

    async def fetch_listings(self, client: httpx.AsyncClient, simulate: bool = False) -> AsyncGenerator[ScrapedProduct, None]:
        try:
            payload = await self.fetch_json(client, simulate=simulate)
        except Exception as exc:
            logger.error(f"Failed to fetch fashionphile listings: {exc}")
            return

        for data in payload:
            url = data.get("product_url", "")
            url_parts = url.strip("/").split("-")
            external_id = data.get("product_id") or (url_parts[-1] if url_parts else url.rsplit("/", 1)[-1])
            name = " ".join(url.split("/")[-1].split("-")[:-1]).title()

            yield ScrapedProduct(
                external_id=str(external_id),
                source="fashionphile",
                title=name or data.get("brand", "Unknown"),
                price=float(data.get("price", 0)),
                currency=data.get("currency", "USD"),
                url=url,
                category=data.get("category", "jewelry"),
                condition=data.get("condition", "Unknown"),
                image_url=(data.get("main_images") or [{}])[0].get("url") if data.get("main_images") else None,
            )
