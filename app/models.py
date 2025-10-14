"""Database models for the application"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles for role-based access control"""

    ADMIN = "admin"
    OPERATOR = "operator"
    READ_ONLY = "read_only"


class User(Base):
    """User model for authentication"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.READ_ONLY, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Device(Base):
    """Network device model"""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    host = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=False)  # cisco_ios, juniper_junos, arista_eos
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)  # Should be encrypted
    secret = Column(
        String(255), nullable=True
    )  # Enable password (None=no enable, ""=enable without password)
    port = Column(Integer, default=22)
    timeout = Column(Integer, default=30)
    session_log = Column(Boolean, default=False)

    # Additional Netmiko ConnectHandler parameters
    global_delay_factor = Column(Integer, default=1, nullable=False)  # Multiplier for all delays
    fast_cli = Column(Boolean, default=False, nullable=False)  # Disable delays for faster execution
    conn_timeout = Column(Integer, default=10, nullable=False)  # TCP connection timeout
    auth_timeout = Column(Integer, nullable=True)  # Authentication timeout
    banner_timeout = Column(Integer, default=15, nullable=False)  # Banner timeout
    read_timeout_override = Column(Integer, nullable=True)  # Override read timeout
    keepalive = Column(Integer, default=0, nullable=False)  # Keepalive interval in seconds

    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', type='{self.device_type}')>"
