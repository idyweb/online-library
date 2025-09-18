"""
Pydantic schemas package.

This package contains all Pydantic schemas for request/response validation
in the online library platform.
"""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenData,
    UserResponse,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserProfile,
)
from app.schemas.author import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
)
from app.schemas.book import (
    BookCreate,
    BookUpdate,
    BookResponse,
)
from app.schemas.reading import (
    ReadingProgressCreate,
    ReadingProgressUpdate,
    ReadingProgressResponse,
    CurrentlyReadingResponse,
    ReadingHistoryResponse,
    BookReadingStatsResponse,
)

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin", 
    "Token",
    "TokenData",
    "UserResponse",
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserProfile",
    # Author schemas
    "AuthorCreate",
    "AuthorUpdate", 
    "AuthorResponse",
    # Book schemas
    "BookCreate",
    "BookUpdate", 
    "BookResponse",
    # Reading schemas
    "ReadingProgressCreate",
    "ReadingProgressUpdate",
    "ReadingProgressResponse",
    "CurrentlyReadingResponse",
    "ReadingHistoryResponse",
    "BookReadingStatsResponse",
]
