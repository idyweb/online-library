"""
Services package.

This package contains business logic services for the online library platform
including authentication, user management, and other core services.
"""

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.reading_service import ReadingService

__all__ = [
    "AuthService",
    "UserService",
    "BookService",
    "ReadingService",
]
