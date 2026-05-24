"""
Authentication and security utilities
Handles password hashing, verification, and input validation
"""

import re
import bcrypt
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password as a string
    """
    if not password:
        raise ValueError("Password cannot be empty")

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password

    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    if not password or not hashed_password:
        return False

    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def validate_input(input_value: str, input_type: str) -> bool:
    """
    Validate input based on type

    Args:
        input_value: The input string to validate
        input_type: The type of input ('username', 'email', 'password')

    Returns:
        True if valid, False otherwise
    """
    if not input_value or not isinstance(input_value, str):
        return False

    if input_type == "username":
        # Username: 3-20 characters, alphanumeric and underscores only
        return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", input_value))

    elif input_type == "email":
        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, input_value))

    elif input_type == "password":
        # Password: at least 8 characters
        return len(input_value) >= 8

    return False


def is_strong_password(password: str) -> tuple[bool, list[str]]:
    """
    Check if password meets strong password requirements

    Args:
        password: The password to check

    Returns:
        Tuple of (is_strong, list_of_issues)
    """
    issues = []

    if len(password) < 12:
        issues.append("Password must be at least 12 characters long")

    if not re.search(r"[A-Z]", password):
        issues.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        issues.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        issues.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")

    return (len(issues) == 0, issues)


def generate_token(user_id: str, secret: str, expiry: int = 3600) -> str:
    """
    Generate a simple token (for demonstration - use JWT in production)

    Args:
        user_id: User identifier
        secret: Secret key for signing
        expiry: Token expiry time in seconds

    Returns:
        Token string
    """
    import hashlib
    import time

    timestamp = int(time.time()) + expiry
    token_data = f"{user_id}:{timestamp}"
    signature = hashlib.sha256(f"{token_data}:{secret}".encode()).hexdigest()

    return f"{token_data}:{signature}"


def verify_token(token: str, secret: str) -> Optional[str]:
    """
    Verify a simple token (for demonstration - use JWT in production)

    Args:
        token: Token string to verify
        secret: Secret key for verification

    Returns:
        User ID if valid, None otherwise
    """
    import hashlib
    import time

    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None

        user_id, timestamp, signature = parts

        # Check expiry
        if int(timestamp) <= int(time.time()):
            return None

        # Verify signature
        token_data = f"{user_id}:{timestamp}"
        expected_signature = hashlib.sha256(
            f"{token_data}:{secret}".encode()
        ).hexdigest()

        if signature != expected_signature:
            return None

        return user_id

    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None
