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

    # Additional Netmiko ConnectHandler parameters
    global_delay_factor: int = Field(
        default=1, ge=1, le=10, description="Multiplier for all delays"
    )
    fast_cli: bool = Field(default=False, description="Disable delays for faster execution")
    conn_timeout: int = Field(
        default=10, ge=1, le=120, description="TCP connection timeout in seconds"
    )
    auth_timeout: Optional[int] = Field(
        default=None, ge=1, le=120, description="Authentication timeout in seconds"
    )
    banner_timeout: int = Field(default=15, ge=1, le=120, description="Banner timeout in seconds")
    read_timeout_override: Optional[int] = Field(
        default=None, ge=1, le=300, description="Override read timeout in seconds"
    )
    keepalive: int = Field(default=0, ge=0, le=300, description="Keepalive interval in seconds")

    description: Optional[str] = None


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""

    password: str = Field(..., min_length=1)
    secret: Optional[str] = Field(
        default=None,
        description="Enable secret: None (no enable mode), empty string (enable without password), or password string",
    )


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
    secret: Optional[str] = Field(
        default=None,
        description="Enable secret: None (no enable mode), empty string (enable without password), or password string",
    )
    port: Optional[int] = Field(None, ge=1, le=65535)
    timeout: Optional[int] = Field(None, ge=1, le=300)
    session_log: Optional[bool] = None

    # Additional Netmiko ConnectHandler parameters
    global_delay_factor: Optional[int] = Field(None, ge=1, le=10)
    fast_cli: Optional[bool] = None
    conn_timeout: Optional[int] = Field(None, ge=1, le=120)
    auth_timeout: Optional[int] = Field(None, ge=1, le=120)
    banner_timeout: Optional[int] = Field(None, ge=1, le=120)
    read_timeout_override: Optional[int] = Field(None, ge=1, le=300)
    keepalive: Optional[int] = Field(None, ge=0, le=300)

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

    # Additional Netmiko ConnectHandler parameters
    global_delay_factor: int
    fast_cli: bool
    conn_timeout: int
    auth_timeout: Optional[int]
    banner_timeout: int
    read_timeout_override: Optional[int]
    keepalive: int

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


# Compliance Schemas
class ComplianceFeature(BaseModel):
    """Schema for a compliance feature definition"""

    name: str = Field(..., description="Feature name (e.g., 'hostname', 'ntp', 'snmp')")
    ordered: bool = Field(default=True, description="Whether section order matters")
    section: list[str] = Field(
        ..., min_items=1, description="Configuration section prefixes to match"
    )


class ComplianceRequest(BaseModel):
    """Schema for configuration compliance check request"""

    features: list[ComplianceFeature] = Field(
        ..., min_items=1, description="List of features to check"
    )
    backup: str = Field(..., min_length=1, description="Backup/current configuration text")
    intended: str = Field(..., min_length=1, description="Intended configuration text")
    network_os: str = Field(..., description="Network OS type (e.g., 'cisco_ios', 'arista_eos')")


class ComplianceFeatureResult(BaseModel):
    """Schema for individual feature compliance result"""

    actual: str = Field(..., description="Actual configuration for this feature")
    intended: str = Field(..., description="Intended configuration for this feature")
    missing: str = Field(..., description="Configuration lines missing from actual")
    extra: str = Field(..., description="Configuration lines extra in actual")
    compliant: bool = Field(..., description="Overall compliance status")
    ordered_compliant: bool = Field(..., description="Compliance with order considered")
    unordered_compliant: bool = Field(..., description="Compliance without order considered")
    cannot_parse: bool = Field(..., description="Whether parsing failed")


class ComplianceResponse(BaseModel):
    """Schema for compliance check response"""

    success: bool
    data: dict[str, ComplianceFeatureResult] = Field(
        ..., description="Compliance results by feature"
    )
    metadata: dict


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime
    version: str
    database: str
