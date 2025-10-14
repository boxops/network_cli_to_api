"""Tests for device management endpoints"""

import pytest
from httpx import AsyncClient
from app.models import Device


@pytest.fixture
async def test_device(db_session):
    """Create test device"""
    device = Device(
        name="test-device",
        host="192.168.1.1",
        device_type="cisco_ios",
        username="admin",
        password="password123",
        port=22,
        timeout=30,
        is_active=True,
    )
    db_session.add(device)
    await db_session.commit()
    await db_session.refresh(device)
    return device


@pytest.mark.asyncio
async def test_list_devices(client: AsyncClient, auth_headers, test_device):
    """Test listing devices"""
    response = await client.get("/devices", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "test-device"


@pytest.mark.asyncio
async def test_create_device(client: AsyncClient, admin_headers):
    """Test creating a device"""
    response = await client.post(
        "/devices",
        headers=admin_headers,
        json={
            "name": "new-device",
            "host": "192.168.1.2",
            "device_type": "cisco_ios",
            "username": "admin",
            "password": "password123",
            "port": 22,
            "timeout": 30,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "new-device"
    assert data["host"] == "192.168.1.2"


@pytest.mark.asyncio
async def test_create_device_non_operator(client: AsyncClient, auth_headers):
    """Test creating device with non-operator user (should fail)"""
    response = await client.post(
        "/devices",
        headers=auth_headers,
        json={
            "name": "new-device",
            "host": "192.168.1.2",
            "device_type": "cisco_ios",
            "username": "admin",
            "password": "password123",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_device(client: AsyncClient, auth_headers, test_device):
    """Test getting device details"""
    response = await client.get(f"/devices/{test_device.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-device"
    assert data["id"] == test_device.id


@pytest.mark.asyncio
async def test_update_device(client: AsyncClient, admin_headers, test_device):
    """Test updating device"""
    response = await client.put(
        f"/devices/{test_device.id}",
        headers=admin_headers,
        json={"description": "Updated description"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_device(client: AsyncClient, admin_headers, test_device):
    """Test deleting device"""
    response = await client.delete(f"/devices/{test_device.id}", headers=admin_headers)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_nonexistent_device(client: AsyncClient, auth_headers):
    """Test getting non-existent device"""
    response = await client.get("/devices/99999", headers=auth_headers)

    assert response.status_code == 404
