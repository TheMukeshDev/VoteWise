"""
Input Validators for VoteWise AI

Validation functions for API inputs.
"""

import re


def validate_email(email):
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength (minimum 8 characters)."""
    return len(password) >= 8


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in data.

    Args:
        data: Dictionary of input data
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = [
        field for field in required_fields if field not in data or not data[field]
    ]
    return len(missing) == 0, missing


def validate_user_id(user_id):
    """Validate user ID format."""
    return user_id and len(str(user_id)) > 0


def validate_faq_id(faq_id):
    """Validate FAQ ID format."""
    return faq_id and len(str(faq_id)) > 0


def validate_timeline_id(timeline_id):
    """Validate timeline ID format."""
    return timeline_id and len(str(timeline_id)) > 0


def sanitize_string(text, max_length=1000):
    """Sanitize string input."""
    if not text:
        return ""
    # Remove leading/trailing whitespace
    text = text.strip()
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    return text
