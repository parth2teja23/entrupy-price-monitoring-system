from __future__ import annotations
from __future__ import annotations
import hashlib
from fastapi import Security, HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from models.security import ApiKey, ApiUsage

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

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