"""Database configuration and session management"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from fastapi import HTTPException, status
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


# Dependency to get database session
async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_device_by_identifier(db: AsyncSession, identifier: str):
    """
    Smart device lookup by ID, name, or IP address.

    Priority order:
    1. If identifier is numeric, try ID lookup
    2. Try name lookup
    3. Try IP address (host) lookup

    Args:
        db: Database session
        identifier: Device ID, name, or IP address

    Returns:
        Device object if found

    Raises:
        HTTPException 404 if device not found
    """
    from app.models import Device

    device = None

    # Try ID lookup if identifier is numeric
    if identifier.isdigit():
        result = await db.execute(select(Device).where(Device.id == int(identifier)))
        device = result.scalar_one_or_none()
        if device:
            return device

    # Try name lookup
    result = await db.execute(select(Device).where(Device.name == identifier))
    device = result.scalar_one_or_none()
    if device:
        return device

    # Try IP address lookup
    result = await db.execute(select(Device).where(Device.host == identifier))
    device = result.scalar_one_or_none()
    if device:
        return device

    # Device not found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Device not found with identifier: {identifier}",
    )
