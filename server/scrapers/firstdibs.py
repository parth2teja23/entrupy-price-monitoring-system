from __future__ import annotations
from __future__ import annotations
import logging
from typing import AsyncGenerator

import httpx

from .base import BaseScraper
from .models import ScrapedProduct

logger = logging.getLogger(__name__)

class FirstDibsScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "1stdibs"

    @property
    def endpoint_path(self) -> str:
        return "/internal/marketplaces/1stdibs"

    async def fetch_listings(self, client: httpx.AsyncClient, simulate: bool = False) -> AsyncGenerator[ScrapedProduct, None]:
        try:
            payload = await self.fetch_json(client, simulate=simulate)
        except Exception as exc:
            logger.error(f"Failed to fetch 1stdibs listings: {exc}")
            return

        for data in payload:
            url = data.get("product_url", "")
            external_id = data.get("product_id") or (url.split("/")[-2] if "id-" in url else url.rsplit("/", 2)[-2] if "/" in url else url)

            yield ScrapedProduct(
                external_id=str(external_id),
                source="1stdibs",
                title=data.get("model", data.get("brand", "Unknown")),
                price=float(data.get("price", 0)),
                currency="USD",
                url=url,
                category=data.get("category", "accessories"),
                condition=data.get("metadata", {}).get("condition") or data.get("condition", "Unknown"),
                image_url=(data.get("main_images") or [{}])[0].get("url") if data.get("main_images") else None,
            )
