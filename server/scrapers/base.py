from __future__ import annotations
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import AsyncGenerator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from scrapers.models import ScrapedProduct


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, httpx.RequestError):
        return True

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        return status_code in {429, 500, 502, 503, 504}

    return False


class BaseScraper(ABC):
    """
    Abstract base specification required by assignment architecture.
    All integration scrapers (Grailed, 1stDibs) must implement these logic rules.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """e.g. 'grailed' or '1stdibs'"""
        pass

    @property
    @abstractmethod
    def endpoint_path(self) -> str:
        """Relative path for the httpx-backed source endpoint."""
        pass

    @abstractmethod
    async def fetch_listings(self, client: httpx.AsyncClient, simulate: bool = False) -> AsyncGenerator[ScrapedProduct, None]:
        """
        Yield ScrapedProduct occurrences from a remote or mocked HTTP source.
        """
        pass

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(_should_retry),
        reraise=True,
    )
    async def fetch_json(self, client: httpx.AsyncClient, simulate: bool = False) -> list[dict]:
        params = {"simulate": "true"} if simulate else None
        response = await client.get(self.endpoint_path, params=params, headers={"Accept": "application/json"})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError(f"Expected a JSON list from {self.endpoint_path}")
        return payload