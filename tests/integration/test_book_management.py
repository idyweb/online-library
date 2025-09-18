"""
Integration tests for book management system.

This module contains comprehensive tests for the book management system
including CRUD operations, search, and authorization.
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


class TestBookManagement:
    """Test cases for the book management system."""
    
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
    
    def test_get_books_empty(self, client):
        """Test getting books when none exist."""
        response = client.get("/books/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["books"] == []
        assert data["total_count"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 100
        assert data["has_more"] is False
    
    def test_get_books_with_pagination(self, client):
        """Test getting books with pagination parameters."""
        response = client.get("/books/?skip=10&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        assert data["skip"] == 10
        assert data["limit"] == 20
    
    def test_get_books_with_genre_filter(self, client):
        """Test getting books with genre filter."""
        response = client.get("/books/?genre=Fiction")
        assert response.status_code == 200
        
        data = response.json()
        assert "books" in data
        assert "total_count" in data
    
    def test_get_books_with_author_filter(self, client):
        """Test getting books with author filter."""
        response = client.get("/books/?author_id=1")
        assert response.status_code == 200
        
        data = response.json()
        assert "books" in data
        assert "total_count" in data
    
    def test_get_nonexistent_book(self, client):
        """Test getting a book that doesn't exist."""
        response = client.get("/books/999")
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]
    
    def test_search_books_empty_query(self, client):
        """Test searching books with empty query."""
        response = client.get("/books/search/?q=")
        assert response.status_code == 422  # Validation error for empty query
    
    def test_search_books_valid_query(self, client):
        """Test searching books with valid query."""
        response = client.get("/books/search/?q=fantasy")
        assert response.status_code == 200
        
        data = response.json()
        assert "books" in data
        assert "total_count" in data
        assert "query" in data
        assert data["query"] == "fantasy"
    
    def test_search_books_with_pagination(self, client):
        """Test searching books with pagination."""
        response = client.get("/books/search/?q=fantasy&skip=5&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["skip"] == 5
        assert data["limit"] == 10
    
    def test_get_author_books_nonexistent_author(self, client):
        """Test getting books for nonexistent author."""
        response = client.get("/books/author/999")
        assert response.status_code == 200
        
        data = response.json()
        assert data["books"] == []
        assert data["total_count"] == 0
        assert data["author_id"] == 999
    
    def test_create_book_unauthorized(self, client):
        """Test creating a book without authentication."""
        book_data = {
            "title": "Test Book",
            "description": "A test book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        response = client.post("/books/", json=book_data)
        assert response.status_code == 403  # No authorization header
    
    def test_create_book_not_author(self, client):
        """Test creating a book as a regular user (not author)."""
        # First register a regular user
        user_data = {
            "username": "regularuser",
            "email": "regular@example.com",
            "password": "SecurePass123!",
            "first_name": "Regular",
            "last_name": "User",
            "is_author": False
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to create a book
        book_data = {
            "title": "Test Book",
            "description": "A test book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/books/", json=book_data, headers=headers)
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_create_book_success(self, client):
        """Test successfully creating a book as an author."""
        # First register an author
        user_data = {
            "username": "testauthor",
            "email": "author@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Create a book
        book_data = {
            "title": "Test Book",
            "description": "A test book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/books/", json=book_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["description"] == "A test book"
        assert data["genre"] == "Fiction"
        assert data["total_pages"] == 200
        assert data["is_published"] is False  # New books start unpublished
        assert data["read_count"] == 0
        assert "id" in data
        assert "author_id" in data
        assert "created_at" in data
    
    def test_create_book_duplicate_title(self, client):
        """Test creating a book with duplicate title for same author."""
        # First register an author
        user_data = {
            "username": "testauthor10",
            "email": "author10@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Create first book
        book_data = {
            "title": "Duplicate Title Book",
            "description": "First book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/books/", json=book_data, headers=headers)
        assert response.status_code == 200
        
        # Try to create second book with same title
        book_data2 = {
            "title": "Duplicate Title Book",
            "description": "Second book",
            "genre": "Non-Fiction",
            "total_pages": 300
        }
        
        response = client.post("/books/", json=book_data2, headers=headers)
        assert response.status_code == 400
        assert "Book with this title already exists" in response.json()["detail"]
    
    def test_create_book_invalid_title(self, client):
        """Test creating a book with invalid title."""
        # First register an author
        user_data = {
            "username": "testauthor3",
            "email": "author3@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to create book with empty title
        book_data = {
            "title": "",
            "description": "A test book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/books/", json=book_data, headers=headers)
        assert response.status_code == 400
        assert "Book title validation failed" in response.json()["detail"]
    
    def test_update_book_unauthorized(self, client):
        """Test updating a book without authentication."""
        book_data = {
            "title": "Updated Book Title"
        }
        
        response = client.put("/books/1", json=book_data)
        assert response.status_code == 403  # No authorization header
    
    def test_update_nonexistent_book(self, client):
        """Test updating a book that doesn't exist."""
        # First register an author
        user_data = {
            "username": "testauthor4",
            "email": "author4@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to update nonexistent book
        book_data = {
            "title": "Updated Book Title"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("/books/999", json=book_data, headers=headers)
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]
    
    def test_update_book_success(self, client):
        """Test successfully updating a book."""
        # First register an author and create a book
        user_data = {
            "username": "testauthor8",
            "email": "author8@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Create a book
        book_data = {
            "title": "Original Title",
            "description": "Original description",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Update the book
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "is_published": True
        }
        
        response = client.put(f"/books/{book_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["is_published"] is True
        assert data["published_at"] is not None
    
    def test_delete_book_unauthorized(self, client):
        """Test deleting a book without authentication."""
        response = client.delete("/books/1")
        assert response.status_code == 403  # No authorization header
    
    def test_delete_nonexistent_book(self, client):
        """Test deleting a book that doesn't exist."""
        # First register an author
        user_data = {
            "username": "testauthor6",
            "email": "author6@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to delete nonexistent book
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("/books/999", headers=headers)
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]
    
    def test_delete_book_success(self, client):
        """Test successfully deleting a book."""
        # First register an author and create a book
        user_data = {
            "username": "testauthor9",
            "email": "author9@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Create a book
        book_data = {
            "title": "Book to Delete",
            "description": "This book will be deleted",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        create_response = client.post("/books/", json=book_data, headers=headers)
        book_id = create_response.json()["id"]
        
        # Delete the book
        response = client.delete(f"/books/{book_id}", headers=headers)
        assert response.status_code == 200
        assert "Book deleted successfully" in response.json()["message"]
        
        # Verify book is deleted
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 404
    
    def test_update_book_wrong_author(self, client):
        """Test updating a book by a different author."""
        # Register first author and create a book
        user_data1 = {
            "username": "author10",
            "email": "author10@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Ten",
            "is_author": True
        }
        register_response1 = client.post("/auth/register", json=user_data1)
        token1 = register_response1.json()["token"]["access_token"]
        
        # Create a book
        book_data = {
            "title": "Author 1's Book",
            "description": "This is author 1's book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        create_response = client.post("/books/", json=book_data, headers=headers1)
        book_id = create_response.json()["id"]
        
        # Register second author
        user_data2 = {
            "username": "author11",
            "email": "author11@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Eleven",
            "is_author": True
        }
        register_response2 = client.post("/auth/register", json=user_data2)
        token2 = register_response2.json()["token"]["access_token"]
        
        # Try to update book with second author's token
        update_data = {
            "title": "Hacked Title"
        }
        
        headers2 = {"Authorization": f"Bearer {token2}"}
        response = client.put(f"/books/{book_id}", json=update_data, headers=headers2)
        assert response.status_code == 403
        assert "Not authorized to update this book" in response.json()["detail"]
    
    def test_delete_book_wrong_author(self, client):
        """Test deleting a book by a different author."""
        # Register first author and create a book
        user_data1 = {
            "username": "author3",
            "email": "author3@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Three",
            "is_author": True
        }
        register_response1 = client.post("/auth/register", json=user_data1)
        token1 = register_response1.json()["token"]["access_token"]
        
        # Create a book
        book_data = {
            "title": "Author 3's Book",
            "description": "This is author 3's book",
            "genre": "Fiction",
            "total_pages": 200
        }
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        create_response = client.post("/books/", json=book_data, headers=headers1)
        book_id = create_response.json()["id"]
        
        # Register second author
        user_data2 = {
            "username": "author4",
            "email": "author4@example.com",
            "password": "SecurePass123!",
            "first_name": "Author",
            "last_name": "Four",
            "is_author": True
        }
        register_response2 = client.post("/auth/register", json=user_data2)
        token2 = register_response2.json()["token"]["access_token"]
        
        # Try to delete book with second author's token
        headers2 = {"Authorization": f"Bearer {token2}"}
        response = client.delete(f"/books/{book_id}", headers=headers2)
        assert response.status_code == 403
        assert "Not authorized to delete this book" in response.json()["detail"]
