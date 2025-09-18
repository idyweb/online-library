"""
Reading Progress model for the online library platform.

This module defines the ReadingProgress model which tracks user reading
progress for books, including current page, reading time, and last read timestamp.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReadingProgress(Base):
    """
    Reading Progress model tracking user reading progress for books.
    
    This model stores information about how far a user has read in a book,
    including current page, total pages, reading time, and last read timestamp.
    Each user can have only one reading progress record per book.
    """
    
    __tablename__ = "reading_progress"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Reading progress information
    current_page: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    total_pages: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    reading_time_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Status flags
    is_completed: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    last_read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reading_progress",
        uselist=False
    )
    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="reading_progress",
        uselist=False
    )
    
    # Unique constraint to ensure one progress record per user-book pair
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='unique_user_book_progress'),
    )
    
    def __repr__(self) -> str:
        """String representation of the ReadingProgress model."""
        return (
            f"<ReadingProgress(id={self.id}, user_id={self.user_id}, "
            f"book_id={self.book_id}, current_page={self.current_page})>"
        )
    
    def update_progress(self, current_page: int, reading_time_minutes: int = 0) -> None:
        """
        Update reading progress for the book.
        
        Args:
            current_page: Current page number
            reading_time_minutes: Additional reading time in minutes
        """
        self.current_page = current_page
        self.reading_time_minutes += reading_time_minutes
        self.last_read_at = datetime.utcnow()
        
        # Check if book is completed
        if self.total_pages and current_page >= self.total_pages:
            self.mark_completed()
    
    def mark_completed(self) -> None:
        """Mark the book as completed."""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        if self.total_pages:
            self.current_page = self.total_pages
    
    def reset_progress(self) -> None:
        """Reset reading progress to the beginning."""
        self.current_page = 1
        self.reading_time_minutes = 0
        self.is_completed = False
        self.completed_at = None
        self.started_at = datetime.utcnow()
        self.last_read_at = None
    
    @property
    def progress_percentage(self) -> float:
        """
        Calculate reading progress as a percentage.
        
        Returns:
            float: Progress percentage (0.0 to 100.0)
        """
        if not self.total_pages or self.total_pages == 0:
            return 0.0
        
        return min(100.0, (self.current_page / self.total_pages) * 100.0)
    
    @property
    def is_started(self) -> bool:
        """
        Check if the user has started reading the book.
        
        Returns:
            bool: True if user has started reading, False otherwise
        """
        return self.current_page > 1 or self.reading_time_minutes > 0
    
    @property
    def reading_time_hours(self) -> float:
        """
        Get reading time in hours.
        
        Returns:
            float: Reading time in hours
        """
        return self.reading_time_minutes / 60.0
