from dataclasses import dataclass
from typing import Optional

@dataclass
class ScrapedProduct:
    """Standardized representation of a product regardless of source marketplace."""
    external_id: str
    source: str
    title: str
    price: float
    currency: str = "USD"
    brand: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    url: str = ""
    image_url: Optional[str] = None
    is_sold: bool = False