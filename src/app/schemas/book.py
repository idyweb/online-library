"""
Book schemas.

This module contains Pydantic schemas for book-related
requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BookCreate(BaseModel):
    """Schema for creating a book."""
    
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Book title"
    )
    description: Optional[str] = Field(
        default=None,
        description="Book description"
    )
    genre: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Book genre"
    )
    total_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Total number of pages"
    )


class BookUpdate(BaseModel):
    """Schema for updating a book."""
    
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Book title"
    )
    description: Optional[str] = Field(
        default=None,
        description="Book description"
    )
    genre: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Book genre"
    )
    total_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Total number of pages"
    )
    is_published: Optional[bool] = Field(
        default=None,
        description="Whether book is published"
    )


class BookResponse(BaseModel):
    """Schema for book response."""
    
    id: int = Field(description="Book ID")
    author_id: int = Field(description="Author ID")
    title: str = Field(description="Book title")
    description: Optional[str] = Field(description="Book description")
    genre: Optional[str] = Field(description="Book genre")
    cover_image_url: Optional[str] = Field(description="Cover image URL")
    file_url: Optional[str] = Field(description="Book file URL")
    file_size: Optional[int] = Field(description="File size in bytes")
    file_type: Optional[str] = Field(description="File type")
    is_published: bool = Field(description="Whether book is published")
    published_at: Optional[datetime] = Field(description="Publication timestamp")
    total_pages: Optional[int] = Field(description="Total number of pages")
    read_count: int = Field(description="Number of reads")
    created_at: datetime = Field(description="Book creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
