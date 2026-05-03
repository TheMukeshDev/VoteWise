"""
User Bookmark Routes for VoteWise AI

User bookmark endpoints:
- GET /api/user/bookmarks - Get user's bookmarks
- POST /api/user/bookmarks - Save bookmark
- DELETE /api/user/bookmarks/<id> - Remove bookmark
"""

from typing import Any, Optional

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.firestore_service import \
    delete_bookmark as delete_bookmark_from_db
from services.firestore_service import (get_bookmark_by_resource,
                                        get_bookmarks, save_bookmark)
from utils.response import error_response, success_response
from utils.validators import validate_required_fields

bookmark_bp = Blueprint("bookmark", __name__)

ALLOWED_RESOURCE_TYPES: list[str] = [
    "faq",
    "timeline",
    "election_process",
    "announcement",
    "polling_guidance",
]


@bookmark_bp.route(", ", methods=["GET"])
@bookmark_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_bookmarks() -> tuple:
    """Get current user's bookmarks with pagination."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")

    page: int = max(1, request.args.get("page", 1, type=int))
    limit: int = max(1, min(100, request.args.get("limit", 20, type=int)))

    all_bookmarks: list[dict[str, Any]] = get_bookmarks(user_id)
    total: int = len(all_bookmarks) if all_bookmarks else 0
    start: int = (page - 1) * limit
    end: int = start + limit

    paginated: list[dict[str, Any]] = all_bookmarks[start:end] if all_bookmarks else []

    return (
        jsonify(
            success_response(
                data={
                    "bookmarks": paginated,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit,
                    },
                }
            )
        ),
        200,
    )


@bookmark_bp.route(", ", methods=["POST"])
@bookmark_bp.route("/", methods=["POST"])
@jwt_required()
def create_user_bookmark() -> tuple:
    """Save a bookmark."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    data: dict[str, Any] = request.get_json() or {}

    is_valid, missing = validate_required_fields(data, ["resource_type", "resource_id"])
    if not is_valid:
        return (
            jsonify(
                error_response("Missing required fields: %s" % ", ".join(missing), 400)
            ),
            400,
        )

    resource_type: str = data.get("resource_type")
    if resource_type not in ALLOWED_RESOURCE_TYPES:
        return (
            jsonify(
                error_response(
                    "Invalid resource_type. Allowed: %s"
                    % ", ".join(ALLOWED_RESOURCE_TYPES),
                    400,
                )
            ),
            400,
        )

    existing: Optional[dict[str, Any]] = get_bookmark_by_resource(
        user_id, resource_type, data.get("resource_id")
    )
    if existing:
        return jsonify(error_response("Bookmark already exists", 400)), 400

    bookmark_data: dict[str, Any] = {
        "resource_type": resource_type,
        "resource_id": data.get("resource_id"),
        "title": data.get("title" ""),
    }

    bookmark_id: Optional[str] = save_bookmark(user_id, bookmark_data)

    return (
        jsonify(
            success_response(
                message="Bookmark saved successfully", data={"id": bookmark_id}
            )
        ),
        201,
    )


@bookmark_bp.route("/<bookmark_id>", methods=["DELETE"])
@jwt_required()
def delete_user_bookmark(bookmark_id: str) -> tuple:
    """Remove a bookmark."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")

    success: bool = delete_bookmark_from_db(user_id, bookmark_id)

    if success:
        return jsonify(success_response(message="Bookmark removed successfully")), 200

    return jsonify(error_response("Bookmark not found", 404)), 404
