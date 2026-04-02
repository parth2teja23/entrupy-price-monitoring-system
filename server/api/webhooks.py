from __future__ import annotations
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import hmac
import hashlib
import secrets

from db.session import get_db
from models.webhook import WebhookSubscription
from api.deps import verify_api_key

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str] = ["price_change"]

class WebhookResponse(BaseModel):
    id: int
    url: str
    secret_key: str
    events: List[str]
    is_active: bool

    model_config = {"from_attributes": True}
@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_in: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    api_key_id: int = Depends(verify_api_key)  # using the raw parsed deps behavior
):
    # Verify that we can treat api_key_id as simple user info. 
    # For now, Webhooks can just be inserted globally or associated with an API Key context if strictly needed
    # but the doc says "Allows users to register" so we usually associate it with the api_key if needed,
    # or just keep it simple.
    
    # generate a random secret for HMAC verification on the client side
    secret_key = secrets.token_urlsafe(32)
    
    new_webhook = WebhookSubscription(
        url=str(webhook_in.url),
        secret_key=secret_key,
        events=webhook_in.events
    )
    
    db.add(new_webhook)
    await db.commit()
    await db.refresh(new_webhook)
    
    return new_webhook

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    result = await db.execute(select(WebhookSubscription).where(WebhookSubscription.is_active == True))
    return result.scalars().all()

@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    result = await db.execute(select(WebhookSubscription).where(WebhookSubscription.id == webhook_id))
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    await db.delete(webhook)
    await db.commit()
    return None
