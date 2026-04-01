from __future__ import annotations
from __future__ import annotations
import pytest
import hmac
import hashlib
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "up"

async def test_unauthorized_access():
    # Construct a raw unauthenticated client pointing to the app instance
    from app.main import create_app
    from httpx import ASGITransport
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/products/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Missing X-API-Key header"
        
        response = await client.get("/api/v1/products/", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid API Key"

async def test_empty_products_list(async_client: AsyncClient):
    response = await async_client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []

async def test_webhook_crud(async_client: AsyncClient):
    # 1. Create a Webhook
    payload = {
        "url": "https://example.com/webhook",
        "events": ["price_change"]
    }
    create_resp = await async_client.post("/api/v1/webhooks/", json=payload)
    assert create_resp.status_code == 201
    webhook_data = create_resp.json()
    assert webhook_data["url"] == "https://example.com/webhook"
    assert webhook_data["is_active"] is True
    assert "secret_key" in webhook_data
    
    webhook_id = webhook_data["id"]

    # 2. List Webhooks
    list_resp = await async_client.get("/api/v1/webhooks/")
    assert list_resp.status_code == 200
    webhooks = list_resp.json()
    assert len(webhooks) == 1
    assert webhooks[0]["id"] == webhook_id

    # 3. Delete Webhook
    del_resp = await async_client.delete(f"/api/v1/webhooks/{webhook_id}")
    assert del_resp.status_code == 204

    # 4. Confirm Deletion
    list_resp_2 = await async_client.get("/api/v1/webhooks/")
    assert list_resp_2.status_code == 200
    assert len(list_resp_2.json()) == 0

async def test_analytics_and_events_empty(async_client: AsyncClient):
    # Tests analytics returns correct blank structure
    analytics_resp = await async_client.get("/api/v1/analytics/")
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert data["total_products"] == 0
    assert data["price_changes_24h"] == 0
    assert data["by_source"] == {}

    # Tests events correctly paginates blank
    events_resp = await async_client.get("/api/v1/events/")
    assert events_resp.status_code == 200
    ev_data = events_resp.json()
    assert ev_data["total"] == 0
    assert ev_data["items"] == []
