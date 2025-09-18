"""
Authentication router.

This module handles authentication-related endpoints including
user registration, login, logout, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    PasswordChange,
)
from app.services.auth_service import AuthService
from app.utils.security import get_current_active_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"}
    }
)


@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        dict: User information and access token
    """
    auth_service = AuthService(db)
    user_response, token_response = await auth_service.register_user(user_data)
    
    return {
        "message": "User registered successfully",
        "user": user_response,
        "token": token_response
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user and return access token.
    
    Args:
        login_data: User login data
        db: Database session
        
    Returns:
        dict: User information and access token
    """
    auth_service = AuthService(db)
    user_response, token_response = await auth_service.login_user(login_data)
    
    return {
        "message": "Login successful",
        "user": user_response,
        "token": token_response
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user (client-side token invalidation).
    
    Note: JWT tokens are stateless, so actual invalidation happens client-side.
    This endpoint is provided for consistency and future token blacklisting.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Logout confirmation message
    """
    return {
        "message": "Logout successful",
        "user_id": current_user.id
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    auth_service = AuthService(db)
    await auth_service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    return {"message": "Password changed successfully"}


@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate user account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    auth_service = AuthService(db)
    await auth_service.deactivate_user(current_user)
    
    return {"message": "Account deactivated successfully"}
