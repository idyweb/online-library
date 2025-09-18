"""
Integration tests for authentication system.

This module contains comprehensive tests for the authentication system
including registration, login, token management, and security features.
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


class TestAuthSystem:
    """Test cases for the authentication system."""
    
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
    
    def test_user_registration_success(self, client):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "is_author": False
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "User registered successfully"
        assert "user" in data
        assert "token" in data
        
        # Check user data
        user = data["user"]
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["first_name"] == "Test"
        assert user["last_name"] == "User"
        assert user["is_author"] is False
        assert user["is_active"] is True
        
        # Check token data
        token = data["token"]
        assert "access_token" in token
        assert token["token_type"] == "bearer"
        assert "expires_in" in token
    
    def test_user_registration_duplicate_username(self, client):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Register first user
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Try to register with same username
        user_data["email"] = "different@example.com"
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_user_registration_duplicate_email(self, client):
        """Test registration with duplicate email."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Register first user
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Try to register with same email
        user_data["username"] = "differentuser"
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_user_registration_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak",  # Too short
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Password validation failed" in response.json()["detail"]
    
    def test_user_registration_invalid_username(self, client):
        """Test registration with invalid username."""
        user_data = {
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username validation failed" in response.json()["detail"]
    
    def test_user_registration_invalid_email(self, client):
        """Test registration with invalid email."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email validation failed" in response.json()["detail"]
    
    def test_user_login_success(self, client):
        """Test successful user login."""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        client.post("/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "username": "testuser",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Login successful"
        assert "user" in data
        assert "token" in data
        
        # Check user data
        user = data["user"]
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        
        # Check token data
        token = data["token"]
        assert "access_token" in token
        assert token["token_type"] == "bearer"
    
    def test_user_login_with_email(self, client):
        """Test login with email instead of username."""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        client.post("/auth/register", json=user_data)
        
        # Login with email
        login_data = {
            "username": "test@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Login successful"
    
    def test_user_login_wrong_password(self, client):
        """Test login with wrong password."""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        client.post("/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "username": "testuser",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_user_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_get_current_user_success(self, client):
        """Test getting current user information."""
        # Register and login
        user_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser2"
        assert data["email"] == "test2@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        assert response.status_code == 403  # No authorization header
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_logout_success(self, client):
        """Test successful logout."""
        # Register and login
        user_data = {
            "username": "testuser3",
            "email": "test3@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Logout successful"
        assert "user_id" in data
    
    def test_author_registration(self, client):
        """Test registration of user as author."""
        user_data = {
            "username": "testauthor2",
            "email": "author2@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "Author",
            "is_author": True
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        user = data["user"]
        assert user["is_author"] is True
    
    def test_password_change_success(self, client):
        """Test successful password change."""
        # Register and login
        user_data = {
            "username": "testuser4",
            "email": "test4@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Change password
        password_data = {
            "current_password": "SecurePass123!",
            "new_password": "NewSecurePass123!"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Password changed successfully"
    
    def test_password_change_wrong_current_password(self, client):
        """Test password change with wrong current password."""
        # Register and login
        user_data = {
            "username": "testuser5",
            "email": "test5@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to change password with wrong current password
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass123!"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_password_change_weak_new_password(self, client):
        """Test password change with weak new password."""
        # Register and login
        user_data = {
            "username": "testuser6",
            "email": "test6@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["token"]["access_token"]
        
        # Try to change password with weak new password
        password_data = {
            "current_password": "SecurePass123!",
            "new_password": "weak"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        assert response.status_code == 400
        assert "New password validation failed" in response.json()["detail"]
