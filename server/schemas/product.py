from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class PriceHistoryOut(BaseModel):
    price: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductOut(BaseModel):
    id: int
    external_id: str
    source: str
    brand: Optional[str] = None
    title: str
    category: Optional[str] = None
    condition: Optional[str] = None
    price: float
    currency: str
    url: str
    image_url: Optional[str] = None
    is_sold: bool
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductDetailOut(ProductOut):
    price_history: List[PriceHistoryOut] = []

class PaginatedProducts(BaseModel):
    total: int
    page: int
    limit: int
    items: List[ProductOut]