"""
API Response Utilities for VoteWise AI

Standardized response format for all API endpoints.
"""

from typing import Any


def success_response(
    data: dict[str, Any] | list[Any] | None = None,
    message: str = "Success",
    code: int = 200,
) -> dict[str, Any]:
    """Create a standardized success response."""
    response: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response


def error_response(message: str = "Error", code: int = 500, errors: list | None = None) -> dict[str, Any]:
    """Create a standardized error response."""
    response: dict[str, Any] = {"success": False, "message": message}
    if errors:
        response["errors"] = errors
    return response


def paginated_response(
    items: list[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "Success",
) -> dict[str, Any]:
    """Create a paginated response."""
    return {
        "success": True,
        "message": message,
        "data": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    }
