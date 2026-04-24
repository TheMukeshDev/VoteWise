"""
User Bookmark Routes for VoteWise AI

User bookmark endpoints:
- GET /api/user/bookmarks - Get user's bookmarks
- POST /api/user/bookmarks - Save bookmark
- DELETE /api/user/bookmarks/<id> - Remove bookmark
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.response import success_response, error_response
from utils.validators import validate_required_fields
from services.firestore_service import (
    get_bookmarks,
    get_bookmark_by_resource,
    save_bookmark,
    delete_bookmark as delete_bookmark_from_db,
)

bookmark_bp = Blueprint("bookmark", __name__)

ALLOWED_RESOURCE_TYPES = [
    "faq",
    "timeline",
    "election_process",
    "announcement",
    "polling_guidance",
]


@bookmark_bp.route("", methods=["GET"])
@bookmark_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_bookmarks():
    """Get current user's bookmarks with pagination."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        page = max(1, page)
        limit = max(1, min(100, limit))

        all_bookmarks = get_bookmarks(user_id)
        total = len(all_bookmarks) if all_bookmarks else 0
        start = (page - 1) * limit
        end = start + limit

        paginated = all_bookmarks[start:end] if all_bookmarks else []

        return jsonify(
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
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@bookmark_bp.route("", methods=["POST"])
@bookmark_bp.route("/", methods=["POST"])
@jwt_required()
def create_user_bookmark():
    """Save a bookmark."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        data = request.get_json() or {}

        is_valid, missing = validate_required_fields(
            data, ["resource_type", "resource_id"]
        )
        if not is_valid:
            return jsonify(
                error_response(f"Missing required fields: {', '.join(missing)}", 400)
            ), 400

        resource_type = data.get("resource_type")
        if resource_type not in ALLOWED_RESOURCE_TYPES:
            return jsonify(
                error_response(
                    f"Invalid resource_type. Allowed: {', '.join(ALLOWED_RESOURCE_TYPES)}",
                    400,
                )
            ), 400

        existing = get_bookmark_by_resource(
            user_id, resource_type, data.get("resource_id")
        )
        if existing:
            return jsonify(error_response("Bookmark already exists", 400)), 400

        bookmark_data = {
            "resource_type": resource_type,
            "resource_id": data.get("resource_id"),
            "title": data.get("title", ""),
        }

        bookmark_id = save_bookmark(user_id, bookmark_data)

        return jsonify(
            success_response(
                message="Bookmark saved successfully", data={"id": bookmark_id}
            )
        ), 201

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@bookmark_bp.route("/<bookmark_id>", methods=["DELETE"])
@jwt_required()
def delete_user_bookmark(bookmark_id):
    """Remove a bookmark."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        success = delete_bookmark_from_db(user_id, bookmark_id)

        if success:
            return jsonify(
                success_response(message="Bookmark removed successfully")
            ), 200

        return jsonify(error_response("Bookmark not found", 404)), 404

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
