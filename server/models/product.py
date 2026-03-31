from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String, index=True, default="unknown", doc="e.g. 1stdibs, fashionphile")
    brand: Mapped[str] = mapped_column(String, index=True)
    model: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    size: Mapped[str | None] = mapped_column(String, nullable=True)
    full_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_url: Mapped[str] = mapped_column(String, unique=True, index=True)
    # Storing the array of image objects directly as JSON for fast delivery/simplicity.
    main_images: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))