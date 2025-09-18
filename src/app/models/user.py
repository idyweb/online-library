"""
User model for the online library platform.

This module defines the User model which represents both regular users
and authors in the system. Users can have different roles and permissions.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """
    User model representing both readers and authors.
    
    This model stores user authentication information and basic profile data.
    Users can be both readers and authors, with the is_author flag indicating
    their author status.
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Authentication fields
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # User status and role
    is_author: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        nullable=False
    )
    
    # Profile information
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    profile_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
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
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # Relationships
    author_profile: Mapped[Optional["Author"]] = relationship(
        "Author",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    reading_progress: Mapped[List["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """
        Get the user's full name.
        
        Returns:
            str: Full name or username if names are not available
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_author_user(self) -> bool:
        """
        Check if user is an author.
        
        Returns:
            bool: True if user is an author, False otherwise
        """
        return self.is_author and self.author_profile is not None
