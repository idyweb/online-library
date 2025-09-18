"""
Book service.

This module contains business logic for book management operations.
"""

from typing import List, Optional, Tuple
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models import Book, Author, User, ReadingProgress
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.utils.validators import validate_book_title


class BookService:
    """Service class for book management operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize book service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_book(
        self, 
        book_data: BookCreate, 
        author: Author
    ) -> BookResponse:
        """
        Create a new book.
        
        Args:
            book_data: Book creation data
            author: Author creating the book
            
        Returns:
            BookResponse: Created book information
            
        Raises:
            HTTPException: If book creation fails
        """
        # Validate book title
        title_issues = validate_book_title(book_data.title)
        if title_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book title validation failed: {', '.join(title_issues)}"
            )
        
        # Check if book with same title already exists for this author
        existing_book = await self.db.execute(
            select(Book).where(
                and_(
                    Book.author_id == author.id,
                    Book.title == book_data.title
                )
            )
        )
        if existing_book.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this title already exists for this author"
            )
        
        # Create new book
        book = Book(
            author_id=author.id,
            title=book_data.title,
            description=book_data.description,
            genre=book_data.genre,
            total_pages=book_data.total_pages,
            is_published=False,  # New books start as unpublished
            read_count=0
        )
        
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        
        # Update author's total books count
        author.total_books += 1
        await self.db.commit()
        
        return BookResponse.model_validate(book)
    
    async def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get book by ID.
        
        Args:
            book_id: Book ID
            
        Returns:
            Optional[Book]: Book if found, None otherwise
        """
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.author).selectinload(Author.user))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()
    
    async def get_books(
        self, 
        skip: int = 0, 
        limit: int = 100,
        published_only: bool = True,
        genre: Optional[str] = None,
        author_id: Optional[int] = None
    ) -> Tuple[List[Book], int]:
        """
        Get list of books with filtering and pagination.
        
        Args:
            skip: Number of books to skip
            limit: Maximum number of books to return
            published_only: Whether to return only published books
            genre: Filter by genre
            author_id: Filter by author ID
            
        Returns:
            Tuple[List[Book], int]: List of books and total count
        """
        # Build query
        query = select(Book).options(
            selectinload(Book.author).selectinload(Author.user)
        )
        
        # Apply filters
        conditions = []
        if published_only:
            conditions.append(Book.is_published == True)
        if genre:
            conditions.append(Book.genre.ilike(f"%{genre}%"))
        if author_id:
            conditions.append(Book.author_id == author_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Book.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Book.created_at.desc())
        result = await self.db.execute(query)
        books = result.scalars().all()
        
        return list(books), total_count
    
    async def update_book(
        self, 
        book: Book, 
        book_data: BookUpdate
    ) -> BookResponse:
        """
        Update book information.
        
        Args:
            book: Book to update
            book_data: Updated book data
            
        Returns:
            BookResponse: Updated book information
            
        Raises:
            HTTPException: If update fails
        """
        # Validate title if provided
        if book_data.title is not None:
            title_issues = validate_book_title(book_data.title)
            if title_issues:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book title validation failed: {', '.join(title_issues)}"
                )
            
            # Check if new title conflicts with existing books
            existing_book = await self.db.execute(
                select(Book).where(
                    and_(
                        Book.author_id == book.author_id,
                        Book.title == book_data.title,
                        Book.id != book.id
                    )
                )
            )
            if existing_book.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Book with this title already exists for this author"
                )
        
        # Update book fields
        if book_data.title is not None:
            book.title = book_data.title
        if book_data.description is not None:
            book.description = book_data.description
        if book_data.genre is not None:
            book.genre = book_data.genre
        if book_data.total_pages is not None:
            book.total_pages = book_data.total_pages
        if book_data.is_published is not None:
            book.is_published = book_data.is_published
            if book_data.is_published and not book.published_at:
                book.published_at = datetime.utcnow()
        
        book.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(book)
        
        return BookResponse.model_validate(book)
    
    async def delete_book(self, book: Book) -> bool:
        """
        Delete a book.
        
        Args:
            book: Book to delete
            
        Returns:
            bool: True if book deleted successfully
        """
        # Get author to update book count
        author = await self.db.get(Author, book.author_id)
        
        # Delete the book
        await self.db.delete(book)
        
        # Update author's total books count
        if author:
            author.total_books = max(0, author.total_books - 1)
        
        await self.db.commit()
        return True
    
    async def search_books(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = True
    ) -> Tuple[List[Book], int]:
        """
        Search books by title, description, or author name.
        
        Args:
            query: Search query
            skip: Number of books to skip
            limit: Maximum number of books to return
            published_only: Whether to return only published books
            
        Returns:
            Tuple[List[Book], int]: List of matching books and total count
        """
        # Build search query
        search_conditions = or_(
            Book.title.ilike(f"%{query}%"),
            Book.description.ilike(f"%{query}%"),
            Book.genre.ilike(f"%{query}%")
        )
        
        # Add published filter if needed
        conditions = [search_conditions]
        if published_only:
            conditions.append(Book.is_published == True)
        
        # Get total count
        count_query = select(func.count(Book.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        
        # Get paginated results
        search_query = (
            select(Book)
            .options(selectinload(Book.author).selectinload(Author.user))
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Book.created_at.desc())
        )
        
        result = await self.db.execute(search_query)
        books = result.scalars().all()
        
        return list(books), total_count
    
    async def increment_read_count(self, book: Book) -> None:
        """
        Increment book read count.
        
        Args:
            book: Book to increment read count for
        """
        book.read_count += 1
        await self.db.commit()
    
    async def get_author_books(
        self, 
        author_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Book], int]:
        """
        Get books by a specific author.
        
        Args:
            author_id: Author ID
            skip: Number of books to skip
            limit: Maximum number of books to return
            
        Returns:
            Tuple[List[Book], int]: List of books and total count
        """
        return await self.get_books(
            skip=skip,
            limit=limit,
            published_only=False,  # Authors can see all their books
            author_id=author_id
        )
