"""
Reading router.

This module handles reading progress-related endpoints including
starting to read books, updating progress, and tracking reading history.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Book, ReadingProgress
from app.schemas.reading import (
    ReadingProgressCreate,
    ReadingProgressUpdate,
    ReadingProgressResponse,
    CurrentlyReadingResponse,
    ReadingHistoryResponse,
    BookReadingStatsResponse,
)
from app.services.reading_service import ReadingService
from app.services.book_service import BookService
from app.utils.security import get_current_active_user

router = APIRouter(
    prefix="/reading",
    tags=["Reading Progress"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"}
    }
)


@router.post("/books/{book_id}/start", response_model=ReadingProgressResponse)
async def start_reading(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start reading a book.
    
    Args:
        book_id: ID of the book to start reading
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ReadingProgressResponse: Reading progress information
        
    Raises:
        HTTPException: If book not found or already being read
    """
    # Get book
    book_service = BookService(db)
    book = await book_service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Start reading
    reading_service = ReadingService(db)
    return await reading_service.start_reading(current_user, book)


@router.put("/books/{book_id}/progress", response_model=ReadingProgressResponse)
async def update_reading_progress(
    book_id: int,
    progress_data: ReadingProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update reading progress for a book.
    
    Args:
        book_id: ID of the book to update progress for
        progress_data: Updated progress data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ReadingProgressResponse: Updated reading progress
        
    Raises:
        HTTPException: If reading progress not found or update invalid
    """
    # Get reading progress
    reading_service = ReadingService(db)
    reading_progress = await reading_service.get_reading_progress(current_user.id, book_id)
    
    if not reading_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found. Start reading the book first."
        )
    
    return await reading_service.update_progress(reading_progress, progress_data)


@router.get("/books/{book_id}/progress", response_model=ReadingProgressResponse)
async def get_reading_progress(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reading progress for a specific book.
    
    Args:
        book_id: ID of the book
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ReadingProgressResponse: Reading progress information
        
    Raises:
        HTTPException: If reading progress not found
    """
    reading_service = ReadingService(db)
    reading_progress = await reading_service.get_reading_progress(current_user.id, book_id)
    
    if not reading_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found"
        )
    
    return ReadingProgressResponse.model_validate(reading_progress)


@router.get("/currently-reading", response_model=List[CurrentlyReadingResponse])
async def get_currently_reading(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get books currently being read by the user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[CurrentlyReadingResponse]: List of currently reading books
    """
    reading_service = ReadingService(db)
    return await reading_service.get_currently_reading(current_user.id)


@router.get("/history", response_model=dict)
async def get_reading_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by reading status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reading history for the user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by reading status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Reading history with pagination info
    """
    reading_service = ReadingService(db)
    progress_list, total_count = await reading_service.get_user_reading_progress(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    # Convert to response format
    history_items = []
    for progress in progress_list:
        history_items.append(ReadingHistoryResponse(
            id=progress.id,
            book_id=progress.book.id,
            book_title=progress.book.title,
            author_name=progress.book.author.display_name,
            is_completed=progress.is_completed,
            current_page=progress.current_page,
            total_pages=progress.book.total_pages,
            progress_percentage=reading_service._calculate_progress_percentage(
                progress.current_page, 
                progress.book.total_pages
            ),
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            last_read_at=progress.last_read_at
        ))
    
    return {
        "history": history_items,
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(history_items) < total_count
    }


@router.get("/books/{book_id}/stats", response_model=BookReadingStatsResponse)
async def get_book_reading_stats(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get reading statistics for a book.
    
    Args:
        book_id: ID of the book
        db: Database session
        
    Returns:
        BookReadingStatsResponse: Reading statistics
        
    Raises:
        HTTPException: If book not found
    """
    # Check if book exists
    book_service = BookService(db)
    book = await book_service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    reading_service = ReadingService(db)
    stats = await reading_service.get_book_reading_stats(book_id)
    
    return BookReadingStatsResponse(**stats)


@router.delete("/books/{book_id}/progress")
async def delete_reading_progress(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete reading progress for a book.
    
    Args:
        book_id: ID of the book
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If reading progress not found
    """
    reading_service = ReadingService(db)
    reading_progress = await reading_service.get_reading_progress(current_user.id, book_id)
    
    if not reading_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found"
        )
    
    await reading_service.delete_reading_progress(reading_progress)
    return {"message": "Reading progress deleted successfully"}