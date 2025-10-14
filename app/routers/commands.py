"""Command execution router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas import CommandRequest, CommandBatchRequest, ConfigUpdateRequest, CommandResponse
from app.models import Device, User
from app.auth import get_current_user, require_operator
from app.services import NetmikoService

router = APIRouter(prefix="/devices", tags=["Command Execution"])


@router.post("/{device_id}/execute", response_model=CommandResponse)
async def execute_command(
    device_id: int,
    command_data: CommandRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a single command on a device
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if not device.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device is not active")

    result = await NetmikoService.execute_command(
        device, command_data.command, command_data.use_textfsm
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Command execution failed"),
        )

    return result


@router.post("/{device_id}/execute-batch", response_model=CommandResponse)
async def execute_commands_batch(
    device_id: int,
    batch_data: CommandBatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute multiple commands on a device
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if not device.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device is not active")

    result = await NetmikoService.execute_commands_batch(
        device, batch_data.commands, batch_data.use_textfsm
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Batch execution failed"),
        )

    return result


@router.get("/{device_id}/config")
async def get_device_config(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get running configuration from a device
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if not device.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device is not active")

    # Determine command based on device type
    config_command = "show running-config"
    if device.device_type == "juniper_junos":
        config_command = "show configuration"

    result = await NetmikoService.execute_command(device, config_command, False)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to retrieve configuration"),
        )

    return result


@router.post("/{device_id}/config", response_model=CommandResponse)
async def update_device_config(
    device_id: int,
    config_data: ConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """
    Update device configuration (Operator or Admin only)
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if not device.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device is not active")

    result = await NetmikoService.send_config_commands(
        device, config_data.commands, config_data.save_config
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Configuration update failed"),
        )

    return result


@router.get("/{device_id}/interfaces")
async def get_device_interfaces(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get interface status from a device (with TextFSM parsing)
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if not device.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device is not active")

    # Determine command based on device type
    interface_command = "show ip interface brief"
    if device.device_type == "juniper_junos":
        interface_command = "show interfaces terse"
    elif device.device_type == "arista_eos":
        interface_command = "show ip interface brief"

    result = await NetmikoService.execute_command(device, interface_command, True)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to retrieve interface status"),
        )

    return result
