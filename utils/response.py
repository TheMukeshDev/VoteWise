"""
API Response Utilities for VoteWise AI

Standardized response format for all API endpoints.
"""


def success_response(data=None, message="Success", code=200):
    """Create a standardized success response."""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response, code


def error_response(message="Error", code=500, errors=None):
    """Create a standardized error response."""
    response = {"success": False, "message": message}
    if errors:
        response["errors"] = errors
    return response, code


def paginated_response(items, page, per_page, total, message="Success"):
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
