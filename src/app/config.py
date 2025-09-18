"""
Application configuration settings.

This module handles all configuration settings for the online library platform,
including database, security, file upload, and application settings.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./online_library.db",
        description="Database connection URL"
    )
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # File Upload Configuration
    max_file_size: int = Field(
        default=10485760,  # 10MB
        description="Maximum file size in bytes"
    )
    upload_dir: str = Field(
        default="./uploads",
        description="Directory for file uploads"
    )
    allowed_extensions: List[str] = Field(
        default=["pdf", "epub", "txt"],
        description="Allowed file extensions for book uploads"
    )
    
    # Application Configuration
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind the application"
    )
    port: int = Field(
        default=8000,
        description="Port to bind the application"
    )
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Returns:
        Settings: Application configuration settings
    """
    return Settings()