"""
Integration tests for database models.

This module contains integration tests that test the models with actual database
operations, including relationships and database constraints.
"""

import pytest
import sys
from sqlalchemy.exc import IntegrityError
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import User, Author, Book, ReadingProgress


class TestModelIntegration:
    """Integration tests for model relationships and database operations."""
    
    @pytest.mark.asyncio
    async def test_user_author_relationship(self, db_session, test_user, test_author):
        """Test the relationship between User and Author models."""
        # Test that author is linked to user
        assert test_author.user_id == test_user.id
        
        # Test that user can access author profile
        # Note: In a real scenario, this would be set by SQLAlchemy relationship
        # For integration tests, we need to test the actual database relationships
    
    @pytest.mark.asyncio
    async def test_author_book_relationship(self, db_session, test_author, test_book):
        """Test the relationship between Author and Book models."""
        # Test that book is linked to author
        assert test_book.author_id == test_author.id
        
        # Test that author can access books
        # This would be tested with actual SQLAlchemy relationships
    
    @pytest.mark.asyncio
    async def test_user_reading_progress_relationship(
        self, db_session, test_user, test_book, test_reading_progress
    ):
        """Test the relationship between User and ReadingProgress models."""
        # Test that reading progress is linked to user and book
        assert test_reading_progress.user_id == test_user.id
        assert test_reading_progress.book_id == test_book.id
    
    @pytest.mark.asyncio
    async def test_unique_user_book_progress_constraint(
        self, db_session, test_user, test_book
    ):
        """Test that each user can only have one reading progress per book."""
        # Create first reading progress
        progress1 = ReadingProgress(
            user_id=test_user.id,
            book_id=test_book.id,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        db_session.add(progress1)
        await db_session.commit()
        
        # Try to create second reading progress for same user-book pair
        progress2 = ReadingProgress(
            user_id=test_user.id,
            book_id=test_book.id,
            current_page=10,
            total_pages=100,
            reading_time_minutes=30,
            is_completed=False
        )
        db_session.add(progress2)
        
        # Should raise IntegrityError due to unique constraint
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_cascade_delete_user_author(self, db_session):
        """Test that deleting a user also deletes their author profile."""
        # Create user and author
        user = User(
            username="cascadeuser",
            email="cascade@example.com",
            password_hash="hashed_password",
            is_author=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        author = Author(
            user_id=user.id,
            pen_name="Cascade Author",
            total_books=0,
            total_reads=0
        )
        db_session.add(author)
        await db_session.commit()
        await db_session.refresh(author)
        
        # Delete user
        await db_session.delete(user)
        await db_session.commit()
        
        # Author should also be deleted due to CASCADE
        result = await db_session.get(Author, author.id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cascade_delete_author_books(self, db_session, test_author):
        """Test that deleting an author also deletes their books."""
        # Create book for author
        book = Book(
            author_id=test_author.id,
            title="Cascade Book",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        db_session.add(book)
        await db_session.commit()
        await db_session.refresh(book)
        
        # Delete author
        await db_session.delete(test_author)
        await db_session.commit()
        
        # Book should also be deleted due to CASCADE
        result = await db_session.get(Book, book.id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cascade_delete_user_reading_progress(
        self, db_session, test_user, test_book
    ):
        """Test that deleting a user also deletes their reading progress."""
        # Create reading progress
        progress = ReadingProgress(
            user_id=test_user.id,
            book_id=test_book.id,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        db_session.add(progress)
        await db_session.commit()
        await db_session.refresh(progress)
        
        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()
        
        # Reading progress should also be deleted due to CASCADE
        result = await db_session.get(ReadingProgress, progress.id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cascade_delete_book_reading_progress(
        self, db_session, test_user, test_book
    ):
        """Test that deleting a book also deletes reading progress for that book."""
        # Create reading progress
        progress = ReadingProgress(
            user_id=test_user.id,
            book_id=test_book.id,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        db_session.add(progress)
        await db_session.commit()
        await db_session.refresh(progress)
        
        # Delete book
        await db_session.delete(test_book)
        await db_session.commit()
        
        # Reading progress should also be deleted due to CASCADE
        result = await db_session.get(ReadingProgress, progress.id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_user_unique_constraints(self, db_session):
        """Test that username and email are unique."""
        # Create first user
        user1 = User(
            username="uniqueuser",
            email="unique@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user1)
        await db_session.commit()
        
        # Try to create second user with same username
        user2 = User(
            username="uniqueuser",  # Same username
            email="different@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
        
        # Reset session
        await db_session.rollback()
        
        # Try to create second user with same email
        user3 = User(
            username="differentuser",
            email="unique@example.com",  # Same email
            password_hash="hashed_password"
        )
        db_session.add(user3)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_author_unique_user_constraint(self, db_session, test_user):
        """Test that each user can only have one author profile."""
        # Create first author profile
        author1 = Author(
            user_id=test_user.id,
            pen_name="First Author",
            total_books=0,
            total_reads=0
        )
        db_session.add(author1)
        await db_session.commit()
        
        # Try to create second author profile for same user
        author2 = Author(
            user_id=test_user.id,  # Same user
            pen_name="Second Author",
            total_books=0,
            total_reads=0
        )
        db_session.add(author2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_model_timestamps_update(self, db_session, test_user):
        """Test that updated_at timestamp is updated when model is modified."""
        original_updated_at = test_user.updated_at
        
        # Wait a small amount to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.01)
        
        # Update user
        test_user.first_name = "Updated Name"
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # updated_at should be different
        assert test_user.updated_at > original_updated_at
        # created_at should remain the same
        assert test_user.created_at == original_updated_at
