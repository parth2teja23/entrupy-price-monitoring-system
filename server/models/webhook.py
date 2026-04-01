from __future__ import annotations
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, unique=True, index=True)
    secret_key: Mapped[str] = mapped_column(String, nullable=False, default="")
    events: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

