from __future__ import annotations
from pydantic import BaseModel, Field, AliasChoices
from typing import Optional

class ScrapedProduct(BaseModel):
    """Standardized representation of a product regardless of source marketplace."""
    external_id: str
    source: str
    title: str = Field(validation_alias=AliasChoices('title', 'name'))
    price: float
    currency: str = "USD"
    brand: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    url: str = ""
    image_url: Optional[str] = None
    is_sold: bool = False