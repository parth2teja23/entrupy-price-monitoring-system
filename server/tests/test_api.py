import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "up"

async def test_create_and_get_product(async_client: AsyncClient):
    new_product_data = {
        "source": "1stdibs",
        "brand": "Chanel",
        "model": "Classic Flap",
        "price": 5500.0,
        "size": "Medium",
        "full_description": "A beautiful classic flap bag.",
        "product_url": "https://example.com/unique-chanel-bag-1",
        "main_images": [
            {"url": "https://example.com/img1.jpg", "format": "jpg"}
        ]
    }
    
    # 1. Create Product
    response = await async_client.post("/api/v1/products/", json=new_product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["brand"] == "Chanel"
    assert data["price"] == 5500.0
    product_id = data["id"]
    
    # 2. Get Product
    response_get = await async_client.get(f"/api/v1/products/{product_id}")
    assert response_get.status_code == 200
    get_data = response_get.json()
    assert get_data["id"] == product_id
    assert get_data["product_url"] == "https://example.com/unique-chanel-bag-1"

async def test_create_duplicate_product_url(async_client: AsyncClient):
    duplicate_data = {
        "source": "fashionphile",
        "brand": "Tiffany",
        "model": "Ring",
        "price": 1000.0,
        "product_url": "https://example.com/unique-chanel-bag-1", # Same URL as previous
    }
    
    # Should conflict because product_url already exists
    response = await async_client.post("/api/v1/products/", json=duplicate_data)
    assert response.status_code == 409