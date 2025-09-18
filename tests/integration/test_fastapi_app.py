"""
Integration tests for FastAPI application.

This module contains tests for the main FastAPI application including
startup, shutdown, middleware, and basic endpoint functionality.
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


class TestFastAPIApp:
    """Test cases for the FastAPI application."""
    
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
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "0.1.0"
        assert "Welcome to Online Library Platform" in data["message"]
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "Online Library Platform is running" in data["message"]
        assert data["version"] == "0.1.0"
    
    def test_docs_endpoint_in_debug_mode(self, client):
        """Test that docs endpoint is available in debug mode."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_endpoint_in_debug_mode(self, client):
        """Test that OpenAPI endpoint is available in debug mode."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Online Library Platform"
    
    def test_auth_endpoints_exist(self, client):
        """Test that auth endpoints exist and return placeholder responses."""
        # Test register endpoint
        response = client.post("/auth/register")
        assert response.status_code == 200
        assert "Registration endpoint" in response.json()["message"]
        
        # Test login endpoint
        response = client.post("/auth/login")
        assert response.status_code == 200
        assert "Login endpoint" in response.json()["message"]
        
        # Test logout endpoint
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert "Logout endpoint" in response.json()["message"]
        
        # Test me endpoint
        response = client.get("/auth/me")
        assert response.status_code == 200
        assert "Current user endpoint" in response.json()["message"]
    
    def test_users_endpoints_exist(self, client):
        """Test that user endpoints exist and return placeholder responses."""
        # Test profile endpoint
        response = client.get("/users/profile")
        assert response.status_code == 200
        assert "User profile endpoint" in response.json()["message"]
        
        # Test update profile endpoint
        response = client.put("/users/profile")
        assert response.status_code == 200
        assert "Update profile endpoint" in response.json()["message"]
        
        # Test reading history endpoint
        response = client.get("/users/reading-history")
        assert response.status_code == 200
        assert "Reading history endpoint" in response.json()["message"]
    
    def test_authors_endpoints_exist(self, client):
        """Test that author endpoints exist and return placeholder responses."""
        # Test authors list endpoint
        response = client.get("/authors/")
        assert response.status_code == 200
        assert "Authors list endpoint" in response.json()["message"]
        
        # Test specific author endpoint
        response = client.get("/authors/1")
        assert response.status_code == 200
        assert "Author 1 endpoint" in response.json()["message"]
        
        # Test author books endpoint
        response = client.get("/authors/1/books")
        assert response.status_code == 200
        assert "Author 1 books endpoint" in response.json()["message"]
        
        # Test update author profile endpoint
        response = client.put("/authors/profile")
        assert response.status_code == 200
        assert "Update author profile endpoint" in response.json()["message"]
    
    def test_books_endpoints_exist(self, client):
        """Test that book endpoints exist and return placeholder responses."""
        # Test books list endpoint
        response = client.get("/books/")
        assert response.status_code == 200
        assert "Books list endpoint" in response.json()["message"]
        
        # Test specific book endpoint
        response = client.get("/books/1")
        assert response.status_code == 200
        assert "Book 1 endpoint" in response.json()["message"]
        
        # Test create book endpoint
        response = client.post("/books/")
        assert response.status_code == 200
        assert "Create book endpoint" in response.json()["message"]
        
        # Test update book endpoint
        response = client.put("/books/1")
        assert response.status_code == 200
        assert "Update book 1 endpoint" in response.json()["message"]
        
        # Test delete book endpoint
        response = client.delete("/books/1")
        assert response.status_code == 200
        assert "Delete book 1 endpoint" in response.json()["message"]
        
        # Test search books endpoint
        response = client.get("/books/search/")
        assert response.status_code == 200
        assert "Search books endpoint" in response.json()["message"]
    
    def test_reading_endpoints_exist(self, client):
        """Test that reading endpoints exist and return placeholder responses."""
        # Test start reading endpoint
        response = client.post("/reading/books/1/start")
        assert response.status_code == 200
        assert "Start reading book 1 endpoint" in response.json()["message"]
        
        # Test update progress endpoint
        response = client.put("/reading/books/1/progress")
        assert response.status_code == 200
        assert "Update progress for book 1 endpoint" in response.json()["message"]
        
        # Test get progress endpoint
        response = client.get("/reading/books/1/progress")
        assert response.status_code == 200
        assert "Get progress for book 1 endpoint" in response.json()["message"]
        
        # Test currently reading endpoint
        response = client.get("/reading/currently-reading")
        assert response.status_code == 200
        assert "Currently reading endpoint" in response.json()["message"]
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        # Test CORS with a GET request that includes Origin header
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        
        # Check that CORS origin header is present
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        
        # Check that credentials are allowed
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
    
    def test_404_endpoint(self, client):
        """Test that non-existent endpoints return 404."""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_app_lifespan(self, async_client):
        """Test that the application lifespan works correctly."""
        # The lifespan should have already run during app creation
        # We can test that the app is working by making a request
        response = await async_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_app_metadata(self, client):
        """Test that the app has correct metadata."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["info"]["title"] == "Online Library Platform"
        assert data["info"]["version"] == "0.1.0"
        assert "modern web application for authors" in data["info"]["description"]
