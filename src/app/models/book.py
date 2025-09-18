"""
Book model for the online library platform.

This module defines the Book model which represents books that authors
can upload and users can read on the platform.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    """
    Book model representing books available on the platform.
    
    This model stores book information including metadata, file references,
    and publication status. Books are linked to authors and can have
    reading progress tracked by users.
    """
    
    __tablename__ = "books"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key to Author
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Book information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    genre: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    # File references
    cover_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    file_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    file_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Publication status
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # Book statistics
    total_pages: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    read_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Timestamps
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
    author: Mapped["Author"] = relationship(
        "Author",
        back_populates="books",
        uselist=False
    )
    reading_progress: Mapped[List["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="book",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the Book model."""
        return f"<Book(id={self.id}, title='{self.title}', author_id={self.author_id})>"
    
    def publish(self) -> None:
        """
        Publish the book.
        
        Sets the book as published and records the publication timestamp.
        """
        self.is_published = True
        self.published_at = datetime.utcnow()
    
    def unpublish(self) -> None:
        """
        Unpublish the book.
        
        Sets the book as unpublished and clears the publication timestamp.
        """
        self.is_published = False
        self.published_at = None
    
    def increment_read_count(self) -> None:
        """Increment the read count for the book."""
        self.read_count += 1
    
    @property
    def is_available(self) -> bool:
        """
        Check if the book is available for reading.
        
        Returns:
            bool: True if book is published and has a file, False otherwise
        """
        return self.is_published and self.file_url is not None
    
    @property
    def file_extension(self) -> Optional[str]:
        """
        Get the file extension from the file URL.
        
        Returns:
            Optional[str]: File extension if available, None otherwise
        """
        if not self.file_url:
            return None
        
        # Extract extension from URL
        return self.file_url.split('.')[-1].lower() if '.' in self.file_url else None
