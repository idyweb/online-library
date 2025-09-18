"""
Unit tests for the User model.

This module contains comprehensive tests for the User model functionality,
including validation, relationships, and business logic.
"""

import pytest
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import User


class TestUserModel:
    """Test cases for the User model."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_author is False  # Default value
        assert user.is_active is True   # Default value
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_full_name_property(self):
        """Test the full_name property."""
        # Test with both first and last name
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )
        assert user.full_name == "John Doe"
        
        # Test with only first name
        user.first_name = "John"
        user.last_name = None
        assert user.full_name == "testuser"  # Falls back to username
        
        # Test with only last name
        user.first_name = None
        user.last_name = "Doe"
        assert user.full_name == "testuser"  # Falls back to username
        
        # Test with no names
        user.first_name = None
        user.last_name = None
        assert user.full_name == "testuser"  # Falls back to username
    
    def test_user_is_author_user_property(self):
        """Test the is_author_user property."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Test when user is not an author
        assert user.is_author_user is False
        
        # Test when user is marked as author but has no author profile
        user.is_author = True
        assert user.is_author_user is False  # No author profile yet
        
        # Test when user has author profile (would be set by relationship)
        # This would be tested in integration tests with actual database
        user.is_author = True
        # Note: author_profile would be set by SQLAlchemy relationship
        # In unit tests, we can't easily test this without database
    
    def test_user_repr(self):
        """Test the string representation of User."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        repr_str = repr(user)
        assert "User" in repr_str
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str
    
    def test_user_validation(self):
        """Test user field validation."""
        # Test required fields
        with pytest.raises((TypeError, ValueError)):
            User()  # Missing required fields
        
        # Test valid user creation
        user = User(
            username="validuser",
            email="valid@example.com",
            password_hash="valid_hash"
        )
        assert user.username == "validuser"
        assert user.email == "valid@example.com"
    
    def test_user_timestamps(self):
        """Test that timestamps are set correctly."""
        before_creation = datetime.utcnow()
        
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        after_creation = datetime.utcnow()
        
        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation
        assert user.created_at == user.updated_at  # Initially same
    
    def test_user_optional_fields(self):
        """Test optional user fields."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            bio="Test bio",
            profile_image_url="https://example.com/image.jpg"
        )
        
        assert user.bio == "Test bio"
        assert user.profile_image_url == "https://example.com/image.jpg"
        assert user.last_login is None  # Should be None initially
    
    def test_user_author_flag(self):
        """Test the is_author flag functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Default should be False
        assert user.is_author is False
        
        # Can be set to True
        user.is_author = True
        assert user.is_author is True
    
    def test_user_active_flag(self):
        """Test the is_active flag functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Default should be True
        assert user.is_active is True
        
        # Can be set to False
        user.is_active = False
        assert user.is_active is False
