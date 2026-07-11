import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_restaurants_returns_list(client: AsyncClient):
    response = await client.get("/restaurants/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data


@pytest.mark.asyncio
async def test_get_restaurants_pagination(client: AsyncClient):
    response = await client.get("/restaurants/", params={"page": 1, "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 5
    assert len(data["items"]) <= 5


@pytest.mark.asyncio
async def test_get_restaurants_search(client: AsyncClient):
    response = await client.get("/restaurants/", params={"q": "pizza"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_get_restaurant_not_found(client: AsyncClient):
    response = await client.get("/restaurants/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_restaurant_requires_auth(client: AsyncClient):
    response = await client.post("/restaurants/create_by_url", json={
        "name": "Test Restaurant",
        "description": "Test",
        "menu": "Pizza; Pasta",
        "main_image": "http://example.com/img.jpg"
    })
    assert response.status_code == 401
