"""
Reading progress schemas.

This module contains Pydantic schemas for reading progress-related
requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ReadingProgressCreate(BaseModel):
    """Schema for creating reading progress."""
    
    book_id: int = Field(
        description="ID of the book to start reading"
    )


class ReadingProgressUpdate(BaseModel):
    """Schema for updating reading progress."""
    
    current_page: Optional[int] = Field(
        default=None,
        ge=1,
        description="Current page number"
    )
    status: Optional[str] = Field(
        default=None,
        description="Reading status (reading, paused, completed, abandoned)"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Reading notes"
    )


class ReadingProgressResponse(BaseModel):
    """Schema for reading progress response."""
    
    id: int = Field(description="Reading progress ID")
    user_id: int = Field(description="User ID")
    book_id: int = Field(description="Book ID")
    current_page: int = Field(description="Current page number")
    total_pages: Optional[int] = Field(description="Total pages in book")
    reading_time_minutes: int = Field(description="Total reading time in minutes")
    is_completed: bool = Field(description="Whether the book is completed")
    started_at: datetime = Field(description="When reading started")
    last_read_at: Optional[datetime] = Field(description="Last read timestamp")
    completed_at: Optional[datetime] = Field(description="When reading was completed")
    created_at: datetime = Field(description="Progress creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class CurrentlyReadingResponse(BaseModel):
    """Schema for currently reading books response."""
    
    book_id: int = Field(description="Book ID")
    book_title: str = Field(description="Book title")
    author_name: str = Field(description="Author name")
    current_page: int = Field(description="Current page number")
    total_pages: Optional[int] = Field(description="Total pages in book")
    progress_percentage: Optional[float] = Field(description="Reading progress percentage")
    last_read_at: Optional[datetime] = Field(description="Last read timestamp")
    started_at: datetime = Field(description="When reading started")
    
    model_config = ConfigDict(from_attributes=True)


class ReadingHistoryResponse(BaseModel):
    """Schema for reading history response."""
    
    id: int = Field(description="Reading progress ID")
    book_id: int = Field(description="Book ID")
    book_title: str = Field(description="Book title")
    author_name: str = Field(description="Author name")
    is_completed: bool = Field(description="Whether the book is completed")
    current_page: int = Field(description="Current page number")
    total_pages: Optional[int] = Field(description="Total pages in book")
    progress_percentage: Optional[float] = Field(description="Reading progress percentage")
    started_at: datetime = Field(description="When reading started")
    completed_at: Optional[datetime] = Field(description="When reading was completed")
    last_read_at: Optional[datetime] = Field(description="Last read timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class BookReadingStatsResponse(BaseModel):
    """Schema for book reading statistics response."""
    
    total_readers: int = Field(description="Total number of readers")
    completed_readers: int = Field(description="Number of completed readers")
    currently_reading: int = Field(description="Number of currently reading users")
    completion_rate: float = Field(description="Completion rate percentage")
    
    model_config = ConfigDict(from_attributes=True)
