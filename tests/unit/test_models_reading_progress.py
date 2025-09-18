"""
Unit tests for the ReadingProgress model.

This module contains comprehensive tests for the ReadingProgress model functionality,
including validation, relationships, and business logic.
"""

import pytest
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import ReadingProgress


class TestReadingProgressModel:
    """Test cases for the ReadingProgress model."""
    
    def test_reading_progress_creation(self):
        """Test basic reading progress creation."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        
        assert progress.user_id == 1
        assert progress.book_id == 1
        assert progress.current_page == 1
        assert progress.total_pages == 100
        assert progress.reading_time_minutes == 0
        assert progress.is_completed is False
        assert isinstance(progress.started_at, datetime)
        assert isinstance(progress.created_at, datetime)
        assert isinstance(progress.updated_at, datetime)
    
    def test_reading_progress_update_progress(self):
        """Test updating reading progress."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        
        # Update progress
        progress.update_progress(50, 30)  # Page 50, 30 minutes
        
        assert progress.current_page == 50
        assert progress.reading_time_minutes == 30
        assert isinstance(progress.last_read_at, datetime)
        assert progress.is_completed is False  # Not at end yet
        
        # Update to completion
        progress.update_progress(100, 15)  # Complete the book
        
        assert progress.current_page == 100
        assert progress.reading_time_minutes == 45  # 30 + 15
        assert progress.is_completed is True
        assert isinstance(progress.completed_at, datetime)
    
    def test_reading_progress_mark_completed(self):
        """Test marking progress as completed."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=50,
            total_pages=100,
            reading_time_minutes=30,
            is_completed=False
        )
        
        progress.mark_completed()
        
        assert progress.is_completed is True
        assert isinstance(progress.completed_at, datetime)
        assert progress.current_page == 100  # Should be set to total_pages
    
    def test_reading_progress_mark_completed_no_total_pages(self):
        """Test marking progress as completed when total_pages is None."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=50,
            total_pages=None,
            reading_time_minutes=30,
            is_completed=False
        )
        
        progress.mark_completed()
        
        assert progress.is_completed is True
        assert isinstance(progress.completed_at, datetime)
        assert progress.current_page == 50  # Should remain unchanged
    
    def test_reading_progress_reset_progress(self):
        """Test resetting reading progress."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=50,
            total_pages=100,
            reading_time_minutes=30,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        
        progress.reset_progress()
        
        assert progress.current_page == 1
        assert progress.reading_time_minutes == 0
        assert progress.is_completed is False
        assert progress.completed_at is None
        assert isinstance(progress.started_at, datetime)
        assert progress.last_read_at is None
    
    def test_reading_progress_progress_percentage(self):
        """Test progress percentage calculation."""
        # Test with valid total pages
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=25,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        assert progress.progress_percentage == 25.0
        
        # Test at 50%
        progress.current_page = 50
        assert progress.progress_percentage == 50.0
        
        # Test at 100%
        progress.current_page = 100
        assert progress.progress_percentage == 100.0
        
        # Test over 100% (should cap at 100)
        progress.current_page = 150
        assert progress.progress_percentage == 100.0
        
        # Test with no total pages
        progress.total_pages = None
        assert progress.progress_percentage == 0.0
        
        # Test with zero total pages
        progress.total_pages = 0
        assert progress.progress_percentage == 0.0
    
    def test_reading_progress_is_started_property(self):
        """Test the is_started property."""
        # Test not started (page 1, no reading time)
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        assert progress.is_started is False
        
        # Test started by page progress
        progress.current_page = 2
        assert progress.is_started is True
        
        # Test started by reading time
        progress.current_page = 1
        progress.reading_time_minutes = 1
        assert progress.is_started is True
    
    def test_reading_progress_reading_time_hours(self):
        """Test reading time in hours conversion."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=60,  # 1 hour
            is_completed=False
        )
        assert progress.reading_time_hours == 1.0
        
        # Test 90 minutes = 1.5 hours
        progress.reading_time_minutes = 90
        assert progress.reading_time_hours == 1.5
        
        # Test 30 minutes = 0.5 hours
        progress.reading_time_minutes = 30
        assert progress.reading_time_hours == 0.5
    
    def test_reading_progress_repr(self):
        """Test the string representation of ReadingProgress."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=25,
            total_pages=100,
            reading_time_minutes=30,
            is_completed=False
        )
        
        repr_str = repr(progress)
        assert "ReadingProgress" in repr_str
        assert "1" in repr_str  # user_id
        assert "1" in repr_str  # book_id
        assert "25" in repr_str  # current_page
    
    def test_reading_progress_optional_fields(self):
        """Test optional reading progress fields."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False,
            last_read_at=datetime.utcnow(),
            completed_at=None
        )
        
        assert progress.last_read_at is not None
        assert progress.completed_at is None
    
    def test_reading_progress_timestamps(self):
        """Test that timestamps are set correctly."""
        before_creation = datetime.utcnow()
        
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        
        after_creation = datetime.utcnow()
        
        assert before_creation <= progress.created_at <= after_creation
        assert before_creation <= progress.updated_at <= after_creation
        assert before_creation <= progress.started_at <= after_creation
        assert progress.created_at == progress.updated_at  # Initially same
    
    def test_reading_progress_validation(self):
        """Test reading progress field validation."""
        # Test required fields
        with pytest.raises((TypeError, ValueError)):
            ReadingProgress()  # Missing required fields
        
        # Test valid reading progress creation
        progress = ReadingProgress(
            user_id=1,
            book_id=1,
            current_page=1,
            total_pages=100,
            reading_time_minutes=0,
            is_completed=False
        )
        assert progress.user_id == 1
        assert progress.book_id == 1
    
    def test_reading_progress_default_values(self):
        """Test default values for reading progress fields."""
        progress = ReadingProgress(
            user_id=1,
            book_id=1
        )
        
        assert progress.current_page == 1
        assert progress.reading_time_minutes == 0
        assert progress.is_completed is False
        assert progress.total_pages is None
        assert progress.last_read_at is None
        assert progress.completed_at is None
