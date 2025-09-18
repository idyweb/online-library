"""
User schemas.

This module contains Pydantic schemas for user-related
requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a user."""
    
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)"
    )
    email: str = Field(
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


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
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
    bio: Optional[str] = Field(
        default=None,
        description="User bio"
    )


class UserProfile(BaseModel):
    """Schema for user profile information."""
    
    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    email: str = Field(description="Email address")
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    bio: Optional[str] = Field(description="User bio")
    is_author: bool = Field(description="Whether user is an author")
    is_active: bool = Field(description="Whether user account is active")
    created_at: datetime = Field(description="Account creation timestamp")
    last_login: Optional[datetime] = Field(description="Last login timestamp")
    
    model_config = ConfigDict(from_attributes=True)
