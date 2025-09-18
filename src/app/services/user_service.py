"""
User service.

This module contains business logic for user management operations.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, Author
from app.schemas.auth import UserResponse


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize user service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_profile(self, user: User) -> UserResponse:
        """
        Get user profile information.
        
        Args:
            user: User object
            
        Returns:
            UserResponse: User profile data
        """
        return UserResponse.model_validate(user)
    
    async def update_user_profile(
        self, 
        user: User, 
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        bio: Optional[str] = None
    ) -> UserResponse:
        """
        Update user profile information.
        
        Args:
            user: User to update
            first_name: New first name
            last_name: New last name
            bio: New bio
            
        Returns:
            UserResponse: Updated user profile
        """
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if bio is not None:
            user.bio = bio
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def get_user_author_profile(self, user: User) -> Optional[Author]:
        """
        Get user's author profile if they are an author.
        
        Args:
            user: User object
            
        Returns:
            Optional[Author]: Author profile if user is an author, None otherwise
        """
        if not user.is_author:
            return None
        
        result = await self.db.execute(
            select(Author).where(Author.user_id == user.id)
        )
        return result.scalar_one_or_none()
    
    async def create_author_profile(
        self, 
        user: User, 
        pen_name: str,
        bio: Optional[str] = None
    ) -> Author:
        """
        Create author profile for a user.
        
        Args:
            user: User to create author profile for
            pen_name: Author's pen name
            bio: Author's bio
            
        Returns:
            Author: Created author profile
        """
        if user.is_author:
            raise ValueError("User already has an author profile")
        
        # Create author profile
        author = Author(
            user_id=user.id,
            pen_name=pen_name,
            bio=bio,
            total_books=0,
            total_reads=0
        )
        
        self.db.add(author)
        
        # Update user to be an author
        user.is_author = True
        
        await self.db.commit()
        await self.db.refresh(author)
        
        return author
