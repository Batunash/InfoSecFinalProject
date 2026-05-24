"""
Utility functions for the application
"""

import html
import logging
import os
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def sanitize_output(output: str) -> str:
    """
    Sanitize output to prevent XSS attacks

    Args:
        output: The string to sanitize

    Returns:
        Sanitized string
    """
    if not output:
        return ""

    return html.escape(str(output))


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """
    Log security-related events

    Args:
        event_type: Type of security event
        details: Dictionary containing event details
    """
    timestamp = datetime.utcnow().isoformat()
    log_entry = {"timestamp": timestamp, "event_type": event_type, "details": details}

    logger.debug(f"Security Event Details: {log_entry}")

    # Log to standard logger
    logger.info(f"Security Event: {event_type} - {details}")

    # In production, you might want to send this to a SIEM system
    # or write to a dedicated security log file


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request

    Args:
        request: Flask request object

    Returns:
        Client IP address
    """
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "unknown"


def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe for redirects

    Args:
        url: URL to check

    Returns:
        True if safe, False otherwise
    """
    if not url:
        return False

    # Prevent open redirects
    if url.startswith(("http://", "https://")):
        # Only allow same-origin redirects
        # In production, configure your allowed domains
        return False

    return True


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging purposes

    Args:
        data: The sensitive data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to keep visible at the end

    Returns:
        Masked string
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""

    return mask_char * (len(data) - visible_chars) + data[-visible_chars:]


def validate_file_upload(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file upload

    Args:
        filename: Name of the uploaded file
        allowed_extensions: Set of allowed file extensions

    Returns:
        True if valid, False otherwise
    """
    if not filename:
        return False

    # Get file extension
    _, ext = os.path.splitext(filename.lower())

    # Check if extension is allowed
    return ext in allowed_extensions


def generate_csrf_token() -> str:
    """
    Generate a CSRF token (for demonstration)

    Returns:
        CSRF token string
    """
    import secrets

    return secrets.token_hex(32)


def rate_limit_key(identifier: str, endpoint: str) -> str:
    """
    Generate a rate limit key

    Args:
        identifier: User identifier (IP, username, etc.)
        endpoint: The endpoint being accessed

    Returns:
        Rate limit key
    """
    return f"rate_limit:{identifier}:{endpoint}"


def parse_user_agent(user_agent: str) -> Dict[str, str]:
    """
    Parse user agent string (basic implementation)

    Args:
        user_agent: User agent string

    Returns:
        Dictionary with parsed information
    """
    if not user_agent:
        return {"browser": "unknown", "os": "unknown"}

    # Basic parsing - in production, use a proper user agent parser
    browser = "unknown"
    os = "unknown"

    ua_lower = user_agent.lower()

    if "chrome" in ua_lower:
        browser = "Chrome"
    elif "firefox" in ua_lower:
        browser = "Firefox"
    elif "safari" in ua_lower:
        browser = "Safari"
    elif "edge" in ua_lower:
        browser = "Edge"

    if "windows" in ua_lower:
        os = "Windows"
    elif "mac" in ua_lower:
        os = "macOS"
    elif "linux" in ua_lower:
        os = "Linux"
    elif "android" in ua_lower:
        os = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os = "iOS"

    return {"browser": browser, "os": os}


def format_error_response(error: str, status_code: int = 500) -> Dict[str, Any]:
    """
    Format a standardized error response

    Args:
        error: Error message
        status_code: HTTP status code

    Returns:
        Formatted error response dictionary
    """
    return {
        "error": error,
        "status": status_code,
        "timestamp": datetime.utcnow().isoformat(),
    }


def format_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Format a standardized success response

    Args:
        data: Response data
        message: Success message

    Returns:
        Formatted success response dictionary
    """
    return {
        "message": message,
        "data": data,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
    }
