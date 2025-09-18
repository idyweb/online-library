"""
Authentication schemas.

This module contains Pydantic schemas for authentication-related
requests and responses including user registration, login, and tokens.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    """Schema for user registration request."""
    
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)"
    )
    email: EmailStr = Field(
        description="Valid email address"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password (8-100 characters)"
    )
    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="First name"
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Last name"
    )
    is_author: bool = Field(
        default=False,
        description="Whether user wants to be an author"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "is_author": False
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login request."""
    
    username: str = Field(
        description="Username or email"
    )
    password: str = Field(
        description="Password"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "securepassword123"
            }
        }
    )


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type"
    )
    expires_in: int = Field(
        description="Token expiration time in seconds"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class TokenData(BaseModel):
    """Schema for JWT token payload data."""
    
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_author: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)."""
    
    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    email: str = Field(description="Email address")
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    is_author: bool = Field(description="Whether user is an author")
    is_active: bool = Field(description="Whether user account is active")
    created_at: datetime = Field(description="Account creation timestamp")
    last_login: Optional[datetime] = Field(description="Last login timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_author": False,
                "is_active": True,
                "created_at": "2025-09-18T20:00:00Z",
                "last_login": "2025-09-18T20:30:00Z"
            }
        }
    )


class PasswordChange(BaseModel):
    """Schema for password change request."""
    
    current_password: str = Field(
        description="Current password"
    )
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password (8-100 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }
    )
