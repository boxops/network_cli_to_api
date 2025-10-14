"""Device management router"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, get_device_by_identifier
from app.schemas import DeviceCreate, DeviceUpdate, DeviceResponse
from app.models import Device, User
from app.auth import get_current_user, require_admin, require_operator
from app.services import NetmikoService

router = APIRouter(prefix="/devices", tags=["Device Management"])


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve list of all devices
    """
    result = await db.execute(select(Device).offset(skip).limit(limit))
    devices = result.scalars().all()
    return devices


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """
    Create a new device (Operator or Admin only)
    """
    # Check if device name already exists
    result = await db.execute(select(Device).where(Device.name == device_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Device name already exists"
        )

    # Create new device
    db_device = Device(**device_data.model_dump())
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)

    return db_device


@router.get("/{device_identifier}", response_model=DeviceResponse)
async def get_device(
    device_identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get device details by ID, name, or IP address
    """
    device = await get_device_by_identifier(db, device_identifier)
    return device


@router.put("/{device_identifier}", response_model=DeviceResponse)
async def update_device(
    device_identifier: str,
    device_data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """
    Update device details by ID, name, or IP address (Operator or Admin only)
    """
    device = await get_device_by_identifier(db, device_identifier)

    # Update device fields
    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    await db.commit()
    await db.refresh(device)

    return device


@router.delete("/{device_identifier}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Delete a device by ID, name, or IP address (Admin only)
    """
    device = await get_device_by_identifier(db, device_identifier)

    await db.delete(device)
    await db.commit()

    return None


@router.post("/{device_identifier}/test")
async def test_device_connection(
    device_identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Test connection to a device by ID, name, or IP address
    """
    device = await get_device_by_identifier(db, device_identifier)

    test_result = await NetmikoService.test_connection(device)

    if not test_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=test_result.get("error", "Connection test failed"),
        )

    return test_result
