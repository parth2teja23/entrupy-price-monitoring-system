from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from scrapers.models import ScrapedProduct

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

    @abstractmethod
    async def fetch_listings(self) -> AsyncGenerator[ScrapedProduct, None]:
        """
        Yield ScrapedProduct occurrences. 
        Must implement tenacity logic handling HTTP 429 timeouts natively in implementation.
        """
        pass