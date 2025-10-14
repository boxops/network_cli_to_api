"""Tests for authentication endpoints"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/auth/login", json={"username": "testuser", "password": "testpassword123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials"""
    response = await client.post(
        "/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers):
    """Test getting current user info"""
    response = await client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_user_admin(client: AsyncClient, admin_headers):
    """Test user registration by admin"""
    response = await client.post(
        "/auth/register",
        headers=admin_headers,
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role": "operator",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "operator"


@pytest.mark.asyncio
async def test_register_user_non_admin(client: AsyncClient, auth_headers):
    """Test user registration by non-admin (should fail)"""
    response = await client.post(
        "/auth/register",
        headers=auth_headers,
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role": "operator",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, auth_headers):
    """Test token refresh"""
    response = await client.post("/auth/refresh", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
