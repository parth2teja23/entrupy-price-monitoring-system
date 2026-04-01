from __future__ import annotations
from __future__ import annotations
import httpx
import logging
import hmac
import hashlib
import json
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from models.webhook import WebhookSubscription
from models.history import PriceChangeEvent
from db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True
)
async def async_post_with_retry(client: httpx.AsyncClient, url: str, payload_bytes: bytes, headers: Dict[str, str]):
    response = await client.post(url, content=payload_bytes, headers=headers)
    response.raise_for_status()
    return response

async def dispatch_webhooks(db: AsyncSession, event_data: Dict[str, Any]):      
    """
    Sends the event payload to all active registered webhooks.
    """
    logger.info("Dispatching webhooks for event data...")

    # Get all active webhooks
    stmt = select(WebhookSubscription).where(WebhookSubscription.is_active == True)
    result = await db.execute(stmt)
    webhooks = result.scalars().all()

    if not webhooks:
        logger.info("No active webhooks configured. Skipping.")
        return

    payload_bytes = json.dumps(event_data).encode("utf-8")

    async with httpx.AsyncClient(timeout=5.0) as client:
        for hook in webhooks:
            # Check if hook is subscribed to this event type
            event_type = event_data.get("event")
            if event_type and event_type not in hook.events:
                continue

            # Create HMAC-SHA256 signature
            signature = hmac.new(
                hook.secret_key.encode("utf-8"),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()

            headers = {
                "Content-Type": "application/json",
                "X-Entrupy-Signature": signature
            }

            try:
                # Utilizes Tenacity for exponential backoff retry logic to handle delivery failures
                response = await async_post_with_retry(client, hook.url, payload_bytes, headers)
                logger.info(f"Successfully dispatched to {hook.url} (Status: {response.status_code})")
            except Exception as e:
                # Eventual delivery failure logged to avoid blocking fetch process
                logger.error(f"Failed to dispatch to {hook.url} after retries: {str(e)}")

async def dispatch_webhooks_with_new_session(event_data: Dict[str, Any]):
    """
    Wrapper to dispatch webhooks within a fresh database session.
    Safe for background tasks.
    """
    async with AsyncSessionLocal() as db:
        await dispatch_webhooks(db, event_data)

