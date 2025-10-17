"""Application Configuration and Settings"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application Info
    app_name: str = "Network API Gateway"
    debug: bool = False
    log_level: str = "INFO"

    # Security
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    database_url: str = "sqlite+aiosqlite:///./network_gateway.db"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Connection Pooling
    max_ssh_connections: int = 50
    ssh_timeout: int = 30

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Default Admin User
    default_admin_username: str = "admin"
    default_admin_password: str = "changeme"
    default_admin_email: str = "admin@example.com"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.strip("[]").split(",")]
        return v


# Global settings instance
settings = Settings()
