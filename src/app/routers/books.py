"""
Books router.

This module handles book-related endpoints including
book discovery, search, and book information.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Author, Book
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.services.book_service import BookService
from app.utils.security import get_current_active_user, get_current_author_user

router = APIRouter(
    prefix="/books",
    tags=["Books"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"}
    }
)


@router.get("/", response_model=dict)
async def get_books(
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of books to return"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of published books with filtering and pagination.
    
    Args:
        skip: Number of books to skip
        limit: Maximum number of books to return
        genre: Filter by genre
        author_id: Filter by author ID
        db: Database session
        
    Returns:
        dict: List of books and pagination info
    """
    book_service = BookService(db)
    books, total_count = await book_service.get_books(
        skip=skip,
        limit=limit,
        published_only=True,
        genre=genre,
        author_id=author_id
    )
    
    return {
        "books": [BookResponse.model_validate(book) for book in books],
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(books) < total_count
    }


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific book information.
    
    Args:
        book_id: ID of the book to retrieve
        db: Database session
        
    Returns:
        BookResponse: Book information
        
    Raises:
        HTTPException: If book not found
    """
    book_service = BookService(db)
    book = await book_service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Only return published books to non-authors
    if not book.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return BookResponse.model_validate(book)


@router.post("/", response_model=BookResponse)
async def create_book(
    book_data: BookCreate,
    current_user: User = Depends(get_current_author_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new book (Author only).
    
    Args:
        book_data: Book creation data
        current_user: Current authenticated author user
        db: Database session
        
    Returns:
        BookResponse: Created book information
        
    Raises:
        HTTPException: If user is not an author or creation fails
    """
    # Get author profile
    from app.services.user_service import UserService
    user_service = UserService(db)
    author = await user_service.get_user_author_profile(current_user)
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author profile not found"
        )
    
    book_service = BookService(db)
    return await book_service.create_book(book_data, author)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: User = Depends(get_current_author_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update book information (Author only).
    
    Args:
        book_id: ID of the book to update
        book_data: Updated book data
        current_user: Current authenticated author user
        db: Database session
        
    Returns:
        BookResponse: Updated book information
        
    Raises:
        HTTPException: If book not found or user not authorized
    """
    book_service = BookService(db)
    book = await book_service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if user is the author of this book
    # We need to get the author profile to check the user_id
    from app.services.user_service import UserService
    user_service = UserService(db)
    author = await user_service.get_user_author_profile(current_user)
    
    if not author or book.author_id != author.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this book"
        )
    
    return await book_service.update_book(book, book_data)


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_author_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a book (Author only).
    
    Args:
        book_id: ID of the book to delete
        current_user: Current authenticated author user
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If book not found or user not authorized
    """
    book_service = BookService(db)
    book = await book_service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if user is the author of this book
    # We need to get the author profile to check the user_id
    from app.services.user_service import UserService
    user_service = UserService(db)
    author = await user_service.get_user_author_profile(current_user)
    
    if not author or book.author_id != author.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this book"
        )
    
    await book_service.delete_book(book)
    return {"message": "Book deleted successfully"}


@router.get("/search/", response_model=dict)
async def search_books(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of books to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search books by title, description, or genre.
    
    Args:
        q: Search query
        skip: Number of books to skip
        limit: Maximum number of books to return
        db: Database session
        
    Returns:
        dict: List of matching books and pagination info
    """
    book_service = BookService(db)
    books, total_count = await book_service.search_books(
        query=q,
        skip=skip,
        limit=limit,
        published_only=True
    )
    
    return {
        "books": [BookResponse.model_validate(book) for book in books],
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(books) < total_count,
        "query": q
    }


@router.get("/author/{author_id}", response_model=dict)
async def get_author_books(
    author_id: int,
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of books to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get books by a specific author.
    
    Args:
        author_id: Author ID
        skip: Number of books to skip
        limit: Maximum number of books to return
        db: Database session
        
    Returns:
        dict: List of author's books and pagination info
    """
    book_service = BookService(db)
    books, total_count = await book_service.get_author_books(
        author_id=author_id,
        skip=skip,
        limit=limit
    )
    
    # Filter to only published books for public access
    published_books = [book for book in books if book.is_published]
    
    return {
        "books": [BookResponse.model_validate(book) for book in published_books],
        "total_count": len(published_books),
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(published_books) < total_count,
        "author_id": author_id
    }
