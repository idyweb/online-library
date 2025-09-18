"""
Users router.

This module handles user-related endpoints including
profile management and user information.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"}
    }
)


@router.get("/profile")
async def get_user_profile():
    """
    Get user profile information.
    
    This endpoint will be implemented with user management.
    """
    return {"message": "User profile endpoint - to be implemented"}


@router.put("/profile")
async def update_user_profile():
    """
    Update user profile information.
    
    This endpoint will be implemented with user management.
    """
    return {"message": "Update profile endpoint - to be implemented"}


@router.get("/reading-history")
async def get_reading_history():
    """
    Get user's reading history.
    
    This endpoint will be implemented with reading progress tracking.
    """
    return {"message": "Reading history endpoint - to be implemented"}
