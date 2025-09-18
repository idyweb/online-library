"""
Author model for the online library platform.

This module defines the Author model which extends user functionality
for authors who can publish books on the platform.
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Author(Base):
    """
    Author model representing authors who can publish books.
    
    This model extends the User model with author-specific information
    such as pen name, bio, and social media links.
    """
    
    __tablename__ = "authors"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key to User
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Author-specific information
    pen_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    profile_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Social media and contact information
    social_links: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict
    )
    
    # Author statistics
    total_books: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    total_reads: Mapped[int] = mapped_column(
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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="author_profile",
        uselist=False
    )
    books: Mapped[List["Book"]] = relationship(
        "Book",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the Author model."""
        return f"<Author(id={self.id}, pen_name='{self.pen_name}', user_id={self.user_id})>"
    
    @property
    def display_name(self) -> str:
        """
        Get the author's display name.
        
        Returns:
            str: Pen name or user's full name if pen name is not set
        """
        return self.pen_name or self.user.full_name
    
    def add_social_link(self, platform: str, url: str) -> None:
        """
        Add a social media link for the author.
        
        Args:
            platform: Social media platform name (e.g., 'twitter', 'instagram')
            url: URL to the social media profile
        """
        if self.social_links is None:
            self.social_links = {}
        self.social_links[platform] = url
    
    def get_social_link(self, platform: str) -> Optional[str]:
        """
        Get a social media link for the author.
        
        Args:
            platform: Social media platform name
            
        Returns:
            Optional[str]: URL if found, None otherwise
        """
        if self.social_links is None:
            return None
        return self.social_links.get(platform)
    
    def increment_book_count(self) -> None:
        """Increment the total books count."""
        self.total_books += 1
    
    def increment_read_count(self) -> None:
        """Increment the total reads count."""
        self.total_reads += 1
