"""
Pytest configuration and fixtures for the online library platform.

This module provides shared fixtures and configuration for all tests.
"""

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.database import Base, get_db
from app.models import User, Author, Book, ReadingProgress


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database for each test function."""
    # Create in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    yield async_session
    
    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db):
    """Provide a database session for tests."""
    async with test_db() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        is_author=False,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_author_user(db_session: AsyncSession) -> User:
    """Create a test user who is also an author."""
    user = User(
        username="testauthor",
        email="author@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Author",
        is_author=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_author(db_session: AsyncSession, test_author_user: User) -> Author:
    """Create a test author."""
    author = Author(
        user_id=test_author_user.id,
        pen_name="Test Author",
        bio="A test author for our library",
        total_books=0,
        total_reads=0
    )
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)
    return author


@pytest_asyncio.fixture
async def test_book(db_session: AsyncSession, test_author: Author) -> Book:
    """Create a test book."""
    book = Book(
        author_id=test_author.id,
        title="Test Book",
        description="A test book for our library",
        genre="Fiction",
        total_pages=100,
        is_published=False,
        read_count=0
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book


@pytest_asyncio.fixture
async def test_reading_progress(
    db_session: AsyncSession, 
    test_user: User, 
    test_book: Book
) -> ReadingProgress:
    """Create a test reading progress."""
    progress = ReadingProgress(
        user_id=test_user.id,
        book_id=test_book.id,
        current_page=1,
        total_pages=test_book.total_pages,
        reading_time_minutes=0,
        is_completed=False
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)
    return progress


@pytest.fixture
def override_get_db(test_db):
    """Override the get_db dependency for testing."""
    async def _override_get_db():
        async with test_db() as session:
            yield session
    
    return _override_get_db
