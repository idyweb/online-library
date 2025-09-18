"""
Unit tests for the Book model.

This module contains comprehensive tests for the Book model functionality,
including validation, relationships, and business logic.
"""

import pytest
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import Book


class TestBookModel:
    """Test cases for the Book model."""
    
    def test_book_creation(self):
        """Test basic book creation."""
        book = Book(
            author_id=1,
            title="Test Book",
            description="A test book for our library",
            genre="Fiction",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        
        assert book.author_id == 1
        assert book.title == "Test Book"
        assert book.description == "A test book for our library"
        assert book.genre == "Fiction"
        assert book.total_pages == 100
        assert book.is_published is False
        assert book.read_count == 0
        assert isinstance(book.created_at, datetime)
        assert isinstance(book.updated_at, datetime)
    
    def test_book_publish(self):
        """Test book publishing functionality."""
        book = Book(
            author_id=1,
            title="Test Book",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        
        assert book.is_published is False
        assert book.published_at is None
        
        book.publish()
        
        assert book.is_published is True
        assert isinstance(book.published_at, datetime)
        assert book.published_at <= datetime.utcnow()
    
    def test_book_unpublish(self):
        """Test book unpublishing functionality."""
        book = Book(
            author_id=1,
            title="Test Book",
            total_pages=100,
            is_published=True,
            published_at=datetime.utcnow(),
            read_count=0
        )
        
        assert book.is_published is True
        assert book.published_at is not None
        
        book.unpublish()
        
        assert book.is_published is False
        assert book.published_at is None
    
    def test_book_increment_read_count(self):
        """Test incrementing read count."""
        book = Book(
            author_id=1,
            title="Test Book",
            total_pages=100,
            is_published=False,
            read_count=5
        )
        
        book.increment_read_count()
        assert book.read_count == 6
        
        book.increment_read_count()
        assert book.read_count == 7
    
    def test_book_is_available_property(self):
        """Test the is_available property."""
        # Test unpublished book
        book = Book(
            author_id=1,
            title="Test Book",
            total_pages=100,
            is_published=False,
            file_url=None,
            read_count=0
        )
        assert book.is_available is False
        
        # Test published book without file
        book.is_published = True
        book.file_url = None
        assert book.is_available is False
        
        # Test published book with file
        book.file_url = "https://example.com/book.pdf"
        assert book.is_available is True
        
        # Test unpublished book with file
        book.is_published = False
        assert book.is_available is False
    
    def test_book_file_extension_property(self):
        """Test the file_extension property."""
        # Test with PDF file
        book = Book(
            author_id=1,
            title="Test Book",
            file_url="https://example.com/book.pdf",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        assert book.file_extension == "pdf"
        
        # Test with EPUB file
        book.file_url = "https://example.com/book.epub"
        assert book.file_extension == "epub"
        
        # Test with no file URL
        book.file_url = None
        assert book.file_extension is None
        
        # Test with file URL without extension
        book.file_url = "https://example.com/book"
        assert book.file_extension is None
        
        # Test with uppercase extension
        book.file_url = "https://example.com/book.PDF"
        assert book.file_extension == "pdf"  # Should be lowercase
    
    def test_book_repr(self):
        """Test the string representation of Book."""
        book = Book(
            author_id=1,
            title="Test Book",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        
        repr_str = repr(book)
        assert "Book" in repr_str
        assert "Test Book" in repr_str
        assert "1" in repr_str  # author_id
    
    def test_book_optional_fields(self):
        """Test optional book fields."""
        book = Book(
            author_id=1,
            title="Test Book",
            description="Test description",
            genre="Fiction",
            cover_image_url="https://example.com/cover.jpg",
            file_url="https://example.com/book.pdf",
            file_size=1024000,  # 1MB
            file_type="pdf",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        
        assert book.description == "Test description"
        assert book.genre == "Fiction"
        assert book.cover_image_url == "https://example.com/cover.jpg"
        assert book.file_url == "https://example.com/book.pdf"
        assert book.file_size == 1024000
        assert book.file_type == "pdf"
        assert book.total_pages == 100
    
    def test_book_timestamps(self):
        """Test that timestamps are set correctly."""
        before_creation = datetime.utcnow()
        
        book = Book(
            author_id=1,
            title="Test Book",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        
        after_creation = datetime.utcnow()
        
        assert before_creation <= book.created_at <= after_creation
        assert before_creation <= book.updated_at <= after_creation
        assert book.created_at == book.updated_at  # Initially same
    
    def test_book_validation(self):
        """Test book field validation."""
        # Test required fields
        with pytest.raises((TypeError, ValueError)):
            Book()  # Missing required fields
        
        # Test valid book creation
        book = Book(
            author_id=1,
            title="Valid Book",
            total_pages=100,
            is_published=False,
            read_count=0
        )
        assert book.title == "Valid Book"
        assert book.author_id == 1
    
    def test_book_default_values(self):
        """Test default values for book fields."""
        book = Book(
            author_id=1,
            title="Test Book"
        )
        
        assert book.is_published is False
        assert book.read_count == 0
        assert book.description is None
        assert book.genre is None
        assert book.cover_image_url is None
        assert book.file_url is None
        assert book.file_size is None
        assert book.file_type is None
        assert book.total_pages is None
        assert book.published_at is None
