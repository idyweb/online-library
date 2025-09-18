"""
Security utilities for authentication and authorization.

This module provides functions for password hashing, JWT token creation
and verification, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas.auth import TokenData

# Get settings
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Optional[TokenData]: Token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        is_author: bool = payload.get("is_author", False)
        
        if username is None or user_id is None:
            return None
            
        return TokenData(
            username=username,
            user_id=user_id,
            is_author=is_author
        )
    except JWTError:
        return None


async def get_user_by_username(
    db: AsyncSession, 
    username: str
) -> Optional[User]:
    """
    Get user by username or email.
    
    Args:
        db: Database session
        username: Username or email
        
    Returns:
        Optional[User]: User if found, None otherwise
    """
    # Try to find by username first
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    # If not found by username, try email
    if user is None:
        result = await db.execute(
            select(User).where(User.email == username)
        )
        user = result.scalar_one_or_none()
    
    return user


async def authenticate_user(
    db: AsyncSession, 
    username: str, 
    password: str
) -> Union[User, bool]:
    """
    Authenticate a user with username/email and password.
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        
    Returns:
        Union[User, bool]: User if authenticated, False otherwise
    """
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        if token_data is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_author_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get the current user if they are an author.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current user if they are an author
        
    Raises:
        HTTPException: If user is not an author
    """
    if not current_user.is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Author access required."
        )
    return current_user


def update_user_last_login(user: User, db: AsyncSession) -> None:
    """
    Update user's last login timestamp.
    
    Args:
        user: User to update
        db: Database session
    """
    user.last_login = datetime.utcnow()
    db.add(user)
