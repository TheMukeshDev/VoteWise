"""
Constants for VoteWise AI.

Centralized constants for consistent messaging, configuration, and validation.
"""

# Error messages (never leak internal details)
ERROR_MESSAGES: dict[str, str] = {
    "required": "{} is required",
    "invalid": "Invalid {}",
    "not_found": "{} not found",
    "unauthorized": "Authentication required",
    "forbidden": "Access denied",
    "server_error": "An unexpected error occurred",
    "rate_limited": "Too many requests. Please try again later.",
    "invalid_input": "Invalid input provided",
}

# Success messages
SUCCESS_MESSAGES: dict[str, str] = {
    "created": "{} created successfully",
    "updated": "{} updated successfully",
    "deleted": "{} deleted successfully",
}

# User roles
USER_ROLES: dict[str, str] = {
    "voter": "voter",
    "admin": "admin",
    "user": "user",
}

# HTTP status codes
STATUS_CODES: dict[str, int] = {
    "success": 200,
    "created": 201,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "rate_limited": 429,
    "server_error": 500,
}

# Supported languages
SUPPORTED_LANGUAGES: list[str] = [
    "en",
    "hi",
    "kn",
    "ta",
    "te",
    "mr",
    "bn",
    "gu",
    "ml",
    "pa",
    "or",
    "as",
    "ur",
]

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
}

# Election types
ELECTION_TYPES: list[str] = [
    "general",
    "state",
    "municipal",
    "panchayat",
    "by-election",
]

# Timeline statuses
TIMELINE_STATUSES: list[str] = [
    "upcoming",
    "ongoing",
    "completed",
    "cancelled",
]

# Announcement priorities
ANNOUNCEMENT_PRIORITIES: list[str] = [
    "low",
    "normal",
    "high",
    "urgent",
]

# Resource types for bookmarks
BOOKMARK_RESOURCE_TYPES: list[str] = [
    "faq",
    "timeline",
    "election_process",
    "announcement",
    "polling_guidance",
]

# Reminder types
REMINDER_TYPES: list[str] = [
    "voting",
    "registration",
    "deadline",
    "event",
    "custom",
]

# API versions
API_VERSIONS: dict[str, str] = {
    "v1": "/api/v1",
}

# FAQ categories
FAQ_CATEGORIES: list[str | None] = [
    None,
    "general",
    "registration",
    "voting",
]
