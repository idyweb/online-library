"""
Validation utilities for user input and data validation.

This module provides functions for validating user input including
passwords, usernames, emails, and other data validation.
"""

import re
from typing import List, Optional


def validate_password_strength(password: str) -> List[str]:
    """
    Validate password strength and return list of issues.
    
    Args:
        password: Password to validate
        
    Returns:
        List[str]: List of validation issues (empty if password is strong)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if len(password) > 100:
        issues.append("Password must be less than 100 characters")
    
    if not re.search(r"[A-Z]", password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        issues.append("Password must contain at least one special character")
    
    return issues


def validate_username(username: str) -> List[str]:
    """
    Validate username format and return list of issues.
    
    Args:
        username: Username to validate
        
    Returns:
        List[str]: List of validation issues (empty if username is valid)
    """
    issues = []
    
    if len(username) < 3:
        issues.append("Username must be at least 3 characters long")
    
    if len(username) > 50:
        issues.append("Username must be less than 50 characters")
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        issues.append("Username can only contain letters, numbers, underscores, and hyphens")
    
    if username.startswith(("-", "_")):
        issues.append("Username cannot start with a hyphen or underscore")
    
    if username.endswith(("-", "_")):
        issues.append("Username cannot end with a hyphen or underscore")
    
    return issues


def validate_email(email: str) -> List[str]:
    """
    Validate email format and return list of issues.
    
    Args:
        email: Email to validate
        
    Returns:
        List[str]: List of validation issues (empty if email is valid)
    """
    issues = []
    
    # Basic email regex pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not re.match(email_pattern, email):
        issues.append("Invalid email format")
    
    if len(email) > 255:
        issues.append("Email must be less than 255 characters")
    
    return issues


def validate_pen_name(pen_name: str) -> List[str]:
    """
    Validate author pen name format and return list of issues.
    
    Args:
        pen_name: Pen name to validate
        
    Returns:
        List[str]: List of validation issues (empty if pen name is valid)
    """
    issues = []
    
    if len(pen_name) < 2:
        issues.append("Pen name must be at least 2 characters long")
    
    if len(pen_name) > 100:
        issues.append("Pen name must be less than 100 characters")
    
    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", pen_name):
        issues.append("Pen name can only contain letters, spaces, hyphens, and apostrophes")
    
    return issues


def validate_book_title(title: str) -> List[str]:
    """
    Validate book title format and return list of issues.
    
    Args:
        title: Book title to validate
        
    Returns:
        List[str]: List of validation issues (empty if title is valid)
    """
    issues = []
    
    if len(title) < 1:
        issues.append("Book title cannot be empty")
    
    if len(title) > 255:
        issues.append("Book title must be less than 255 characters")
    
    # Allow letters, numbers, spaces, and common punctuation
    if not re.match(r"^[a-zA-Z0-9\s\-'.,!?()]+$", title):
        issues.append("Book title contains invalid characters")
    
    return issues


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension against allowed extensions.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed file extensions
        
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        bool: True if file size is within limits, False otherwise
    """
    return file_size <= max_size


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "file"
    
    return sanitized
