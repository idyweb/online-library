"""
API routers package.

This package contains all FastAPI routers for the online library platform.
"""

from app.routers import auth, users, authors, books, reading

__all__ = ["auth", "users", "authors", "books", "reading"]
