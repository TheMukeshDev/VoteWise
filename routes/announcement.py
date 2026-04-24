"""
Announcement Routes for VoteWise AI

Admin announcement management endpoints:
- GET /api/admin/announcements - Get all announcements (admin)
- GET /api/admin/announcements/<id> - Get specific announcement (admin)
- POST /api/admin/announcements - Create announcement (admin)
- PUT /api/admin/announcements/<id> - Update announcement (admin)
- DELETE /api/admin/announcements/<id> - Delete announcement (admin)
"""

from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_admin
from utils.response import success_response, error_response
from utils.validators import validate_required_fields
from services.announcement_service import announcement_service
from config import Config

announcement_bp = Blueprint("announcement", __name__)

ALLOWED_PRIORITIES = ["low", "normal", "high", "urgent"]


@announcement_bp.route("", methods=["GET"])
@announcement_bp.route("/", methods=["GET"])
@require_admin
def get_announcements():
    """Get all announcements (admin)."""
    try:
        region = request.args.get("region")
        priority = request.args.get("priority")

        announcements = announcement_service.get_all_for_admin()

        if region:
            announcements = [a for a in announcements if a.get("region") == region]
        if priority:
            announcements = [a for a in announcements if a.get("priority") == priority]

        return jsonify(success_response(data=announcements)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@announcement_bp.route("/<announcement_id>", methods=["GET"])
@require_admin
def get_announcement(announcement_id):
    """Get a specific announcement (admin)."""
    try:
        announcement = announcement_service.get_by_id(announcement_id)

        if not announcement:
            return jsonify(error_response("Announcement not found", 404)), 404

        return jsonify(success_response(data=announcement)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@announcement_bp.route("", methods=["POST"])
@announcement_bp.route("/", methods=["POST"])
@require_admin
def create_announcement():
    """Create a new announcement (admin only)."""
    try:
        data = request.get_json() or {}

        is_valid, missing = validate_required_fields(data, ["title", "message"])
        if not is_valid:
            return jsonify(
                error_response(f"Missing required fields: {', '.join(missing)}", 400)
            ), 400

        priority = data.get("priority", "normal")
        if priority not in ALLOWED_PRIORITIES:
            return jsonify(
                error_response(
                    f"Invalid priority. Allowed: {', '.join(ALLOWED_PRIORITIES)}", 400
                )
            ), 400

        announcement = announcement_service.create(
            title=data["title"],
            message=data["message"],
            priority=priority,
            region=data.get("region", "all"),
            is_active=data.get("is_active", True),
        )

        return jsonify(
            success_response(
                message="Announcement created successfully", data=announcement
            )
        ), 201

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@announcement_bp.route("/<announcement_id>", methods=["PUT"])
@require_admin
def update_announcement(announcement_id):
    """Update an announcement (admin only)."""
    try:
        data = request.get_json() or {}

        if "priority" in data and data["priority"] not in ALLOWED_PRIORITIES:
            return jsonify(
                error_response(
                    f"Invalid priority. Allowed: {', '.join(ALLOWED_PRIORITIES)}", 400
                )
            ), 400

        announcement = announcement_service.update(announcement_id, data)

        if not announcement:
            return jsonify(error_response("Announcement not found", 404)), 404

        return jsonify(
            success_response(
                message="Announcement updated successfully", data=announcement
            )
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@announcement_bp.route("/<announcement_id>", methods=["DELETE"])
@require_admin
def delete_announcement(announcement_id):
    """Delete an announcement (admin only)."""
    try:
        success = announcement_service.delete(announcement_id)

        if not success:
            return jsonify(error_response("Announcement not found", 404)), 404

        return jsonify(
            success_response(message="Announcement deleted successfully")
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
