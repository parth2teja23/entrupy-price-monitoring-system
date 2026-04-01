from __future__ import annotations
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class ApiUsage(Base):
    __tablename__ = "api_usage"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    api_key_id: Mapped[int] = mapped_column(ForeignKey("api_keys.id", ondelete="CASCADE"), index=True)
    endpoint: Mapped[str] = mapped_column(String)
    method: Mapped[str] = mapped_column(String)
    status_code: Mapped[int] = mapped_column(Integer)
    called_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))