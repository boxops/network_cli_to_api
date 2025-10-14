"""Pydantic schemas for request/response validation"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: Literal["admin", "operator", "read_only"] = "read_only"


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "operator", "read_only"]] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Schema for user response"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Device Schemas
class DeviceBase(BaseModel):
    """Base device schema"""

    name: str = Field(..., min_length=1, max_length=100)
    host: str = Field(..., min_length=1, max_length=255)
    device_type: Literal[
        "cisco_ios",
        "cisco_nxos",
        "cisco_xe",
        "cisco_asa",
        "juniper_junos",
        "arista_eos",
        "hp_procurve",
        "paloalto_panos",
        "fortinet",
        "generic",
    ]
    username: str = Field(..., min_length=1, max_length=100)
    port: int = Field(default=22, ge=1, le=65535)
    timeout: int = Field(default=30, ge=1, le=300)
    session_log: bool = False
    description: Optional[str] = None


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""

    password: str = Field(..., min_length=1)
    secret: Optional[str] = None


class DeviceUpdate(BaseModel):
    """Schema for updating a device"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    device_type: Optional[
        Literal[
            "cisco_ios",
            "cisco_nxos",
            "cisco_xe",
            "cisco_asa",
            "juniper_junos",
            "arista_eos",
            "hp_procurve",
            "paloalto_panos",
            "fortinet",
            "generic",
        ]
    ] = None
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=1)
    secret: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    timeout: Optional[int] = Field(None, ge=1, le=300)
    session_log: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DeviceResponse(BaseModel):
    """Schema for device response (excludes sensitive data)"""

    id: int
    name: str
    host: str
    device_type: str
    username: str
    port: int
    timeout: int
    session_log: bool
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Authentication Schemas
class Token(BaseModel):
    """JWT token response"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""

    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""

    username: str
    password: str


# Command Execution Schemas
class CommandRequest(BaseModel):
    """Schema for command execution request"""

    command: str = Field(..., min_length=1)
    use_textfsm: bool = False


class CommandBatchRequest(BaseModel):
    """Schema for batch command execution"""

    commands: list[str] = Field(..., min_items=1)
    use_textfsm: bool = False


class ConfigUpdateRequest(BaseModel):
    """Schema for configuration update"""

    commands: list[str] = Field(..., min_items=1)
    save_config: bool = True


class CommandResponse(BaseModel):
    """Schema for command execution response"""

    success: bool
    data: dict
    metadata: dict


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime
    version: str
    database: str
