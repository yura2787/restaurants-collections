import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/users/create", json={
        "email": "newuser@example.com",
        "name": "NewUser",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "NewUser"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "name": "User", "password": "pass12345"}
    await client.post("/users/create", json=payload)
    response = await client.post("/users/create", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    response = await client.post("/users/create", json={
        "email": "short@example.com",
        "name": "User",
        "password": "123"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_unverified_user(client: AsyncClient, registered_user):
    response = await client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_login_wrong_credentials(client: AsyncClient):
    response = await client.post("/auth/login", data={
        "username": "nobody@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_returns_same_error_for_wrong_email_and_wrong_password(client: AsyncClient, registered_user):
    resp_no_user = await client.post("/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "anypassword"
    })
    resp_wrong_pass = await client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert resp_no_user.status_code == resp_wrong_pass.status_code == 401
