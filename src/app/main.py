"""
Main FastAPI application for the online library platform.

This module creates and configures the FastAPI application with all necessary
middleware, routes, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.routers import auth, users, authors, books, reading


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events for the FastAPI application.
    This replaces the deprecated @app.on_event decorators.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control back to the application
    """
    # Startup
    print("🚀 Starting Online Library Platform...")
    await init_db()
    print("✅ Database initialized successfully")
    print("📚 Online Library Platform is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Online Library Platform...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Create FastAPI app with lifespan management
    app = FastAPI(
        title="Online Library Platform",
        description="A modern web application for authors to upload books and readers to access them online",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for security
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
        )
    
    # Add custom exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler for unexpected errors."""
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "internal_error"
            }
        )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.
        
        Returns:
            dict: Application health status
        """
        return {
            "status": "healthy",
            "message": "Online Library Platform is running",
            "version": "0.1.0"
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint with API information.
        
        Returns:
            dict: API information and available endpoints
        """
        return {
            "message": "Welcome to Online Library Platform",
            "version": "0.1.0",
            "docs": "/docs" if settings.debug else "Documentation not available in production",
            "health": "/health"
        }
    
    # Include routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(authors.router)
    app.include_router(books.router)
    app.include_router(reading.router)
    
    return app


# Create the application instance
app = create_app()
