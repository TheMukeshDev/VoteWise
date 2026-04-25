"""
Constants for VoteWise AI.

Centralized constants for consistent messaging and configuration.
"""

ERROR_MESSAGES = {
    "required": "{} is required",
    "invalid": "Invalid {}",
    "not_found": "{} not found",
    "unauthorized": "Authentication required",
    "forbidden": "Access denied",
    "server_error": "An unexpected error occurred",
}

SUCCESS_MESSAGES = {
    "created": "{} created successfully",
    "updated": "{} updated successfully",
    "deleted": "{} deleted successfully",
}

USER_ROLES = {
    "voter": "voter",
    "admin": "admin",
}

STATUS_CODES = {
    "success": 200,
    "created": 201,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "server_error": 500,
}

API_VERSIONS = {
    "v1": "/api/v1",
}
