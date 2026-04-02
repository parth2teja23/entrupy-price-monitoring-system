from __future__ import annotations
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Security, HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from db.session import get_db
from models.security import ApiKey, ApiUsage

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Allows 60 requests per minute
RATE_LIMIT_BPM = 60

async def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header"
        )

    # Hash incoming key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Query database for exact match
    result = await db.execute(select(ApiKey).where(ApiKey.key_hash == key_hash))
    db_key = result.scalar_one_or_none()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    # Rate Limit Evaluation (Trailing Minute)
    one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    rate_stmt = select(func.count(ApiUsage.id)).where(
        ApiUsage.api_key_id == db_key.id,
        ApiUsage.called_at >= one_min_ago
    )
    request_count = await db.scalar(rate_stmt)

    if request_count and request_count >= RATE_LIMIT_BPM:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate Limit Exceeded. Try again later."
        )

    # Log the successful usage
    usage = ApiUsage(
        api_key_id=db_key.id,
        endpoint=request.url.path,
        method=request.method,
        status_code=200 # Placeholder for baseline middleware tracking
    )
    db.add(usage)
    await db.commit()
    
    return db_key