"""
Authentication service.

This module contains business logic for user authentication including
registration, login, and token management.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models import User, Author
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_user_by_username,
)
from app.utils.validators import (
    validate_password_strength,
    validate_username,
    validate_email,
)

# Get settings
settings = get_settings()


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize authentication service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def register_user(self, user_data: UserRegister) -> Tuple[UserResponse, Token]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple[UserResponse, Token]: User response and access token
            
        Raises:
            HTTPException: If registration fails
        """
        # Validate input data
        await self._validate_registration_data(user_data)
        
        # Check if user already exists
        existing_user = await get_user_by_username(self.db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        existing_user = await get_user_by_username(self.db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_author=user_data.is_author,
            is_active=True
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Create author profile if user is an author
        if user_data.is_author:
            author = Author(
                user_id=user.id,
                pen_name=user_data.first_name or user_data.username,
                total_books=0,
                total_reads=0
            )
            self.db.add(author)
            await self.db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "is_author": user.is_author
            }
        )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Create response objects
        user_response = UserResponse.model_validate(user)
        token_response = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
        return user_response, token_response
    
    async def login_user(self, login_data: UserLogin) -> Tuple[UserResponse, Token]:
        """
        Authenticate and login a user.
        
        Args:
            login_data: User login data
            
        Returns:
            Tuple[UserResponse, Token]: User response and access token
            
        Raises:
            HTTPException: If login fails
        """
        # Find user by username or email
        user = await get_user_by_username(self.db, login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "is_author": user.is_author
            }
        )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Create response objects
        user_response = UserResponse.model_validate(user)
        token_response = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
        return user_response, token_response
    
    async def _validate_registration_data(self, user_data: UserRegister) -> None:
        """
        Validate user registration data.
        
        Args:
            user_data: User registration data
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate username
        username_issues = validate_username(user_data.username)
        if username_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username validation failed: {', '.join(username_issues)}"
            )
        
        # Validate email
        email_issues = validate_email(user_data.email)
        if email_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email validation failed: {', '.join(email_issues)}"
            )
        
        # Validate password strength
        password_issues = validate_password_strength(user_data.password)
        if password_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_issues)}"
            )
    
    async def change_password(
        self, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user: User to change password for
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            HTTPException: If password change fails
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        password_issues = validate_password_strength(new_password)
        if password_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password validation failed: {', '.join(password_issues)}"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        await self.db.commit()
        
        return True
    
    async def deactivate_user(self, user: User) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user: User to deactivate
            
        Returns:
            bool: True if user deactivated successfully
        """
        user.is_active = False
        await self.db.commit()
        return True
