from uuid import uuid4

from httpx import AsyncClient


async def test_register_user(client: AsyncClient):
    unique = uuid4().hex
    payload = {
        "email": f"user_{unique}@example.com",
        "username": f"user_{unique}",
        "password": "123456",
    }

    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["username"] == payload["username"]
    assert data["user"]["role"] == "CUSTOMER"
    assert data["token"]["token_type"] == "bearer"
    assert "access_token" in data["token"]


async def test_login_user(client: AsyncClient):
    unique = uuid4().hex

    payload = {
        "email": f"login_{unique}@example.com",
        "username": f"login_{unique}",
        "password": "123456",
    }

    register_response = await client.post("/api/v1/auth/register", json=payload)

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert data["user"]["email"] == payload["email"]
    assert data["token"]["token_type"] == "bearer"
    assert "access_token" in data["token"]


async def test_login_with_wrong_password_returns_unauthorized(client: AsyncClient):
    unique = uuid4().hex

    payload = {
        "email": f"wrong_{unique}@example.com",
        "username": f"wrong_{unique}",
        "password": "123456",
    }

    register_response = await client.post("/api/v1/auth/register", json=payload)

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": "wrong-password",
        },
    )

    assert login_response.status_code == 401

    data = login_response.json()

    assert data["error"]["code"] == "UNAUTHORIZED"
    assert data["error"]["message"] == "Invalid email or password"
