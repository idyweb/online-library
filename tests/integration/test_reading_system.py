"""
Integration tests for reading progress system.

This module contains comprehensive tests for the reading progress system
including starting to read, updating progress, and tracking history.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.main import create_app


class TestReadingSystem:
    """Test cases for the reading progress system."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        return create_app()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest_asyncio.fixture
    async def async_client(self, app):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    def test_start_reading_unauthorized(self, client):
        """Test starting to read without authentication."""
        response = client.post("/reading/books/1/start")
        assert response.status_code == 403  # No authorization header
    
    def test_start_reading_nonexistent_book(self, client):
        """Test starting to read a book that doesn't exist."""
        # First register a user
        user_data = {
            "username": "reader1",
            "email": "reader1@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "One"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to start reading nonexistent book
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/reading/books/999/start", headers=headers)
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]
    
    def test_start_reading_unpublished_book(self, client):
        """Test starting to read an unpublished book."""
        # First register an author and create an unpublished book
        user_data = {
            "username": "author1",
            "email": "author1@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "One",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create an unpublished book
        book_data = {
            "title": "Unpublished Book",
            "description": "This book is not published",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Register a reader
        reader_data = {
            "username": "reader2",
            "email": "reader2@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Two"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Try to start reading unpublished book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 400
        assert "Cannot start reading an unpublished book" in response.json()["detail"]
    
    def test_start_reading_success(self, client):
        """Test successfully starting to read a book."""
        # First register an author and create a published book
        user_data = {
            "username": "readingauthor3",
            "email": "readingauthor3@example.com",
            "password": "SecurePass123!",
            "first_name": "Reading",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Published Book",
            "description": "This book is published",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Register a reader
        reader_data = {
            "username": "readingreader3",
            "email": "readingreader3@example.com",
            "password": "SecurePass123!",
            "first_name": "Reading",
            "last_name": "Reader"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == register_response.json()["user"]["id"]
        assert data["book_id"] == book_id
        assert data["current_page"] == 1
        assert data["is_completed"] == False
        assert data["started_at"] is not None
    
    def test_start_reading_already_reading(self, client):
        """Test starting to read a book that's already being read."""
        # First register an author and create a published book
        user_data = {
            "username": "author3",
            "email": "author3@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Three",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Another Published Book",
            "description": "This book is published",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Register a reader
        reader_data = {
            "username": "reader4",
            "email": "reader4@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Four"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        # Try to start reading the same book again
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 400
        assert "User is already reading this book" in response.json()["detail"]
    
    def test_update_progress_unauthorized(self, client):
        """Test updating progress without authentication."""
        progress_data = {"current_page": 10}
        response = client.put("/reading/books/1/progress", json=progress_data)
        assert response.status_code == 403  # No authorization header
    
    def test_update_progress_not_found(self, client):
        """Test updating progress for a book not being read."""
        # Register a user
        user_data = {
            "username": "reader5",
            "email": "reader5@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Five"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to update progress for a book not being read
        progress_data = {"current_page": 10}
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("/reading/books/1/progress", json=progress_data, headers=headers)
        assert response.status_code == 404
        assert "Reading progress not found" in response.json()["detail"]
    
    def test_update_progress_success(self, client):
        """Test successfully updating reading progress."""
        # First register an author and create a published book
        user_data = {
            "username": "author4",
            "email": "author4@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Four",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Progress Test Book",
            "description": "This book is for testing progress",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Register a reader
        reader_data = {
            "username": "reader6",
            "email": "reader6@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Six"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        # Update progress
        progress_data = {
            "current_page": 50
        }
        response = client.put(f"/reading/books/{book_id}/progress", json=progress_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["current_page"] == 50
        assert data["is_completed"] == False
    
    def test_update_progress_invalid_page(self, client):
        """Test updating progress with invalid page number."""
        # First register an author and create a published book
        user_data = {
            "username": "author5",
            "email": "author5@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Five",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Page Test Book",
            "description": "This book is for testing page validation",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Register a reader
        reader_data = {
            "username": "reader7",
            "email": "reader7@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Seven"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        # Try to update with invalid page number
        progress_data = {"current_page": 0}  # Invalid: less than 1
        response = client.put(f"/reading/books/{book_id}/progress", json=progress_data, headers=headers)
        assert response.status_code == 400
        assert "Current page must be at least 1" in response.json()["detail"]
        
        # Try to update with page exceeding total pages
        progress_data = {"current_page": 300}  # Invalid: exceeds total pages
        response = client.put(f"/reading/books/{book_id}/progress", json=progress_data, headers=headers)
        assert response.status_code == 400
        assert "Current page cannot exceed total pages" in response.json()["detail"]
    
    def test_complete_reading(self, client):
        """Test completing a book."""
        # First register an author and create a published book
        user_data = {
            "username": "author6",
            "email": "author6@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Six",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Completion Test Book",
            "description": "This book is for testing completion",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Register a reader
        reader_data = {
            "username": "reader8",
            "email": "reader8@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Eight"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        # Complete the book
        progress_data = {
            "current_page": 200,
            "status": "completed"
        }
        response = client.put(f"/reading/books/{book_id}/progress", json=progress_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["current_page"] == 200
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
    
    def test_get_currently_reading_empty(self, client):
        """Test getting currently reading books when none exist."""
        # Register a user
        user_data = {
            "username": "reader9",
            "email": "reader9@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Nine"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Get currently reading books
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/reading/currently-reading", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data == []
    
    def test_get_currently_reading_with_books(self, client):
        """Test getting currently reading books."""
        # First register an author and create a published book
        user_data = {
            "username": "author7",
            "email": "author7@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Seven",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Currently Reading Test Book",
            "description": "This book is for testing currently reading",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Register a reader
        reader_data = {
            "username": "reader10",
            "email": "reader10@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Ten"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        # Get currently reading books
        response = client.get("/reading/currently-reading", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["book_id"] == book_id
        assert data[0]["book_title"] == "Currently Reading Test Book"
        assert data[0]["current_page"] == 1
        assert data[0]["total_pages"] == 200
        assert data[0]["progress_percentage"] == 0.5  # 1/200 * 100
    
    def test_get_reading_history_empty(self, client):
        """Test getting reading history when none exists."""
        # Register a user
        user_data = {
            "username": "reader11",
            "email": "reader11@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Eleven"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Get reading history
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/reading/history", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["history"] == []
        assert data["total_count"] == 0
    
    def test_get_book_reading_stats(self, client):
        """Test getting book reading statistics."""
        # First register an author and create a published book
        user_data = {
            "username": "author8",
            "email": "author8@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Eight",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        author_token = register_response.json()["token"]["access_token"]
        
        # Create and publish a book
        book_data = {
            "title": "Stats Test Book",
            "description": "This book is for testing stats",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {author_token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Publish the book
        update_data = {"is_published": True}
        client.put(f"/books/{book_id}", json=update_data, headers=headers)
        
        # Get book reading stats (should be empty initially)
        response = client.get(f"/reading/books/{book_id}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_readers"] == 0
        assert data["completed_readers"] == 0
        assert data["currently_reading"] == 0
        assert data["completion_rate"] == 0.0
        
        # Register a reader and start reading
        reader_data = {
            "username": "reader12",
            "email": "reader12@example.com",
            "password": "SecurePass123!",
            "first_name": "Reader",
            "last_name": "Twelve"
        }
        register_response = client.post("/auth/register", json=reader_data)
        reader_token = register_response.json()["token"]["access_token"]
        
        # Start reading the book
        headers = {"Authorization": f"Bearer {reader_token}"}
        response = client.post(f"/reading/books/{book_id}/start", headers=headers)
        assert response.status_code == 200
        
        # Get book reading stats again
        response = client.get(f"/reading/books/{book_id}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_readers"] == 1
        assert data["completed_readers"] == 0
        assert data["currently_reading"] == 1
        assert data["completion_rate"] == 0.0
