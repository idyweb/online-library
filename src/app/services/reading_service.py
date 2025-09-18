"""
Reading progress service.

This module contains business logic for reading progress tracking operations.
"""

from typing import List, Optional, Tuple
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models import ReadingProgress, Book, User, Author
from app.schemas.reading import (
    ReadingProgressCreate,
    ReadingProgressUpdate,
    ReadingProgressResponse,
    CurrentlyReadingResponse,
)


class ReadingService:
    """Service class for reading progress management operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize reading service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def start_reading(
        self, 
        user: User, 
        book: Book
    ) -> ReadingProgressResponse:
        """
        Start reading a book for a user.
        
        Args:
            user: User starting to read
            book: Book to start reading
            
        Returns:
            ReadingProgressResponse: Reading progress information
            
        Raises:
            HTTPException: If book is not published or already being read
        """
        # Check if book is published
        if not book.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot start reading an unpublished book"
            )
        
        # Check if user is already reading this book
        existing_progress = await self.db.execute(
            select(ReadingProgress).where(
                and_(
                    ReadingProgress.user_id == user.id,
                    ReadingProgress.book_id == book.id
                )
            )
        )
        if existing_progress.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already reading this book"
            )
        
        # Create new reading progress
        reading_progress = ReadingProgress(
            user_id=user.id,
            book_id=book.id,
            current_page=1,
            total_pages=book.total_pages,
            is_completed=False
        )
        
        self.db.add(reading_progress)
        await self.db.commit()
        await self.db.refresh(reading_progress)
        
        # Increment book read count
        await self._increment_book_read_count(book)
        
        return ReadingProgressResponse.model_validate(reading_progress)
    
    async def update_progress(
        self, 
        reading_progress: ReadingProgress, 
        progress_data: ReadingProgressUpdate
    ) -> ReadingProgressResponse:
        """
        Update reading progress for a user.
        
        Args:
            reading_progress: Current reading progress
            progress_data: Updated progress data
            
        Returns:
            ReadingProgressResponse: Updated reading progress
            
        Raises:
            HTTPException: If progress update is invalid
        """
        # Validate current page
        if progress_data.current_page is not None:
            if progress_data.current_page < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current page must be at least 1"
                )
            
            # Get book to check total pages
            book = await self.db.get(Book, reading_progress.book_id)
            if book and book.total_pages and progress_data.current_page > book.total_pages:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Current page cannot exceed total pages ({book.total_pages})"
                )
        
        # Update progress fields
        if progress_data.current_page is not None:
            reading_progress.current_page = progress_data.current_page
        
        if progress_data.status is not None:
            if progress_data.status == "completed":
                reading_progress.is_completed = True
                reading_progress.completed_at = datetime.utcnow()
            elif progress_data.status == "reading":
                reading_progress.is_completed = False
                reading_progress.last_read_at = datetime.utcnow()
        
        # Update last_read_at for any progress update
        reading_progress.last_read_at = datetime.utcnow()
        
        reading_progress.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(reading_progress)
        
        return ReadingProgressResponse.model_validate(reading_progress)
    
    async def get_reading_progress(
        self, 
        user_id: int, 
        book_id: int
    ) -> Optional[ReadingProgress]:
        """
        Get reading progress for a specific user and book.
        
        Args:
            user_id: User ID
            book_id: Book ID
            
        Returns:
            Optional[ReadingProgress]: Reading progress if found, None otherwise
        """
        result = await self.db.execute(
            select(ReadingProgress)
            .options(
                selectinload(ReadingProgress.book).selectinload(Book.author).selectinload(Author.user)
            )
            .where(
                and_(
                    ReadingProgress.user_id == user_id,
                    ReadingProgress.book_id == book_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_reading_progress(
        self, 
        user_id: int, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[ReadingProgress], int]:
        """
        Get all reading progress for a user with optional filtering.
        
        Args:
            user_id: User ID
            status: Filter by reading status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple[List[ReadingProgress], int]: List of reading progress and total count
        """
        # Build query
        query = select(ReadingProgress).options(
            selectinload(ReadingProgress.book).selectinload(Book.author).selectinload(Author.user)
        ).where(ReadingProgress.user_id == user_id)
        
        # Apply status filter
        if status == "completed":
            query = query.where(ReadingProgress.is_completed == True)
        elif status == "reading":
            query = query.where(ReadingProgress.is_completed == False)
        
        # Get total count
        count_query = select(func.count(ReadingProgress.id)).where(ReadingProgress.user_id == user_id)
        if status == "completed":
            count_query = count_query.where(ReadingProgress.is_completed == True)
        elif status == "reading":
            count_query = count_query.where(ReadingProgress.is_completed == False)
        
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(ReadingProgress.updated_at.desc())
        result = await self.db.execute(query)
        progress_list = result.scalars().all()
        
        return list(progress_list), total_count
    
    async def get_currently_reading(
        self, 
        user_id: int
    ) -> List[CurrentlyReadingResponse]:
        """
        Get books currently being read by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[CurrentlyReadingResponse]: List of currently reading books
        """
        result = await self.db.execute(
            select(ReadingProgress)
            .options(
                selectinload(ReadingProgress.book).selectinload(Book.author).selectinload(Author.user)
            )
            .where(
                and_(
                    ReadingProgress.user_id == user_id,
                    ReadingProgress.is_completed == False
                )
            )
            .order_by(ReadingProgress.last_read_at.desc())
        )
        progress_list = result.scalars().all()
        
        return [
            CurrentlyReadingResponse(
                book_id=progress.book.id,
                book_title=progress.book.title,
                author_name=progress.book.author.display_name,
                current_page=progress.current_page,
                total_pages=progress.book.total_pages,
                progress_percentage=self._calculate_progress_percentage(
                    progress.current_page, 
                    progress.book.total_pages
                ),
                last_read_at=progress.last_read_at,
                started_at=progress.started_at
            )
            for progress in progress_list
        ]
    
    async def get_reading_history(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[ReadingProgress], int]:
        """
        Get reading history for a user (completed and abandoned books).
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple[List[ReadingProgress], int]: List of reading history and total count
        """
        return await self.get_user_reading_progress(
            user_id=user_id,
            status="completed",
            skip=skip,
            limit=limit
        )
    
    async def get_book_reading_stats(
        self, 
        book_id: int
    ) -> dict:
        """
        Get reading statistics for a book.
        
        Args:
            book_id: Book ID
            
        Returns:
            dict: Reading statistics
        """
        # Get total readers
        total_readers_result = await self.db.execute(
            select(func.count(ReadingProgress.id.distinct())).where(
                ReadingProgress.book_id == book_id
            )
        )
        total_readers = total_readers_result.scalar()
        
        # Get completed readers
        completed_readers_result = await self.db.execute(
            select(func.count(ReadingProgress.id.distinct())).where(
                and_(
                    ReadingProgress.book_id == book_id,
                    ReadingProgress.is_completed == True
                )
            )
        )
        completed_readers = completed_readers_result.scalar()
        
        # Get currently reading
        currently_reading_result = await self.db.execute(
            select(func.count(ReadingProgress.id.distinct())).where(
                and_(
                    ReadingProgress.book_id == book_id,
                    ReadingProgress.is_completed == False
                )
            )
        )
        currently_reading = currently_reading_result.scalar()
        
        # Get average completion rate
        completion_rate = (completed_readers / total_readers * 100) if total_readers > 0 else 0
        
        return {
            "total_readers": total_readers,
            "completed_readers": completed_readers,
            "currently_reading": currently_reading,
            "completion_rate": round(completion_rate, 2)
        }
    
    async def delete_reading_progress(
        self, 
        reading_progress: ReadingProgress
    ) -> bool:
        """
        Delete reading progress.
        
        Args:
            reading_progress: Reading progress to delete
            
        Returns:
            bool: True if deleted successfully
        """
        await self.db.delete(reading_progress)
        await self.db.commit()
        return True
    
    def _calculate_progress_percentage(
        self, 
        current_page: int, 
        total_pages: Optional[int]
    ) -> Optional[float]:
        """
        Calculate reading progress percentage.
        
        Args:
            current_page: Current page number
            total_pages: Total pages in book
            
        Returns:
            Optional[float]: Progress percentage if total_pages is available
        """
        if not total_pages or total_pages <= 0:
            return None
        
        return round((current_page / total_pages) * 100, 2)
    
    async def _increment_book_read_count(self, book: Book) -> None:
        """
        Increment book read count.
        
        Args:
            book: Book to increment read count for
        """
        book.read_count += 1
        await self.db.commit()
