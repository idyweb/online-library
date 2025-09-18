"""
Unit tests for the Author model.

This module contains comprehensive tests for the Author model functionality,
including validation, relationships, and business logic.
"""

import pytest
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import Author


class TestAuthorModel:
    """Test cases for the Author model."""
    
    def test_author_creation(self):
        """Test basic author creation."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            bio="A test author for our library",
            total_books=0,
            total_reads=0
        )
        
        assert author.user_id == 1
        assert author.pen_name == "Test Author"
        assert author.bio == "A test author for our library"
        assert author.total_books == 0
        assert author.total_reads == 0
        assert isinstance(author.created_at, datetime)
        assert isinstance(author.updated_at, datetime)
    
    def test_author_display_name_property(self):
        """Test the display_name property."""
        # Test with pen name
        author = Author(
            user_id=1,
            pen_name="Pen Name",
            total_books=0,
            total_reads=0
        )
        assert author.display_name == "Pen Name"
        
        # Test with empty pen name (would fall back to user.full_name in real app)
        author.pen_name = ""
        assert author.display_name == ""  # In unit test, can't access user relationship
    
    def test_author_social_links(self):
        """Test social links functionality."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            total_books=0,
            total_reads=0
        )
        
        # Test adding social links
        author.add_social_link("twitter", "https://twitter.com/testauthor")
        author.add_social_link("instagram", "https://instagram.com/testauthor")
        
        assert author.social_links["twitter"] == "https://twitter.com/testauthor"
        assert author.social_links["instagram"] == "https://instagram.com/testauthor"
        
        # Test getting social links
        assert author.get_social_link("twitter") == "https://twitter.com/testauthor"
        assert author.get_social_link("instagram") == "https://instagram.com/testauthor"
        assert author.get_social_link("facebook") is None  # Non-existent platform
    
    def test_author_social_links_none_initial(self):
        """Test social links when initially None."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            social_links=None,
            total_books=0,
            total_reads=0
        )
        
        # Should handle None gracefully
        assert author.get_social_link("twitter") is None
        
        # Adding a link should initialize the dict
        author.add_social_link("twitter", "https://twitter.com/testauthor")
        assert author.social_links["twitter"] == "https://twitter.com/testauthor"
    
    def test_author_increment_book_count(self):
        """Test incrementing book count."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            total_books=5,
            total_reads=0
        )
        
        author.increment_book_count()
        assert author.total_books == 6
        
        author.increment_book_count()
        assert author.total_books == 7
    
    def test_author_increment_read_count(self):
        """Test incrementing read count."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            total_books=0,
            total_reads=10
        )
        
        author.increment_read_count()
        assert author.total_reads == 11
        
        author.increment_read_count()
        assert author.total_reads == 12
    
    def test_author_repr(self):
        """Test the string representation of Author."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            total_books=0,
            total_reads=0
        )
        
        repr_str = repr(author)
        assert "Author" in repr_str
        assert "Test Author" in repr_str
        assert "1" in repr_str  # user_id
    
    def test_author_optional_fields(self):
        """Test optional author fields."""
        author = Author(
            user_id=1,
            pen_name="Test Author",
            bio="Test bio",
            profile_image_url="https://example.com/author.jpg",
            total_books=0,
            total_reads=0
        )
        
        assert author.bio == "Test bio"
        assert author.profile_image_url == "https://example.com/author.jpg"
    
    def test_author_timestamps(self):
        """Test that timestamps are set correctly."""
        before_creation = datetime.utcnow()
        
        author = Author(
            user_id=1,
            pen_name="Test Author",
            total_books=0,
            total_reads=0
        )
        
        after_creation = datetime.utcnow()
        
        assert before_creation <= author.created_at <= after_creation
        assert before_creation <= author.updated_at <= after_creation
        assert author.created_at == author.updated_at  # Initially same
    
    def test_author_validation(self):
        """Test author field validation."""
        # Test required fields
        with pytest.raises((TypeError, ValueError)):
            Author()  # Missing required fields
        
        # Test valid author creation
        author = Author(
            user_id=1,
            pen_name="Valid Author",
            total_books=0,
            total_reads=0
        )
        assert author.pen_name == "Valid Author"
        assert author.user_id == 1
    
    def test_author_default_values(self):
        """Test default values for author fields."""
        author = Author(
            user_id=1,
            pen_name="Test Author"
        )
        
        assert author.total_books == 0
        assert author.total_reads == 0
        assert author.bio is None
        assert author.profile_image_url is None
        assert author.social_links == {}
