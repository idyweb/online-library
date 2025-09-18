"""
Author schemas.

This module contains Pydantic schemas for author-related
requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field, ConfigDict


class AuthorCreate(BaseModel):
    """Schema for creating an author profile."""
    
    pen_name: str = Field(
        min_length=2,
        max_length=100,
        description="Author's pen name"
    )
    bio: Optional[str] = Field(
        default=None,
        description="Author's bio"
    )


class AuthorUpdate(BaseModel):
    """Schema for updating an author profile."""
    
    pen_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Author's pen name"
    )
    bio: Optional[str] = Field(
        default=None,
        description="Author's bio"
    )
    social_links: Optional[Dict[str, str]] = Field(
        default=None,
        description="Social media links"
    )


class AuthorResponse(BaseModel):
    """Schema for author response."""
    
    id: int = Field(description="Author ID")
    user_id: int = Field(description="User ID")
    pen_name: str = Field(description="Author's pen name")
    bio: Optional[str] = Field(description="Author's bio")
    profile_image_url: Optional[str] = Field(description="Profile image URL")
    social_links: Optional[Dict[str, str]] = Field(description="Social media links")
    total_books: int = Field(description="Total number of books")
    total_reads: int = Field(description="Total number of reads")
    created_at: datetime = Field(description="Author profile creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
