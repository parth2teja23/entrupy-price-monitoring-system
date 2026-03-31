from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class ProductBase(BaseModel):
    source: str
    brand: str
    model: str
    price: float
    size: Optional[str] = None
    full_description: Optional[str] = None
    product_url: str
    main_images: Optional[List[dict]] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    price: Optional[float] = None
    size: Optional[str] = None
    full_description: Optional[str] = None
    main_images: Optional[List[dict]] = None

class ProductInDB(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)