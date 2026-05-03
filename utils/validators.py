"""
Input Validators for VoteWise AI

Validation functions for API inputs.
"""

import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password strength (minimum 8 characters)."""
    return len(password) >= 8


def validate_required_fields(data: dict, required_fields: list[str]) -> tuple[bool, list[str]]:
    """
    Validate that all required fields are present in data.

    Args:
        data: Dictionary of input data
        required_fields: list of required field names

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = [field for field in required_fields if field not in data or not data[field]]
    return len(missing) == 0, missing


def validate_user_id(user_id: str) -> bool:
    """Validate user ID format."""
    return user_id and len(str(user_id)) > 0


def validate_faq_id(faq_id: str) -> bool:
    """Validate FAQ ID format."""
    return faq_id and len(str(faq_id)) > 0


def validate_timeline_id(timeline_id: str) -> bool:
    """Validate timeline ID format."""
    return timeline_id and len(str(timeline_id)) > 0


def validate_language(language: str, allowed: list[str] | None = None) -> bool:
    """Validate language code."""
    if not language:
        return False
    if allowed:
        return language in allowed
    return len(language) == 2


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize string input."""
    if not text:
        return ", "
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text
