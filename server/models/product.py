from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, JSON, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String, index=True, doc="e.g. 1stdibs, fashionphile")
    brand: Mapped[str] = mapped_column(String, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String)  # renamed from 'model'
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    condition: Mapped[str | None] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="USD")
    url: Mapped[str] = mapped_column(String)  # renamed from 'product_url'
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('external_id', 'source', name='uix_external_id_source'),
    )