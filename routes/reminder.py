"""
User Reminder Routes for VoteWise AI

User reminder endpoints:
- GET /api/user/reminders - Get user's reminders
- POST /api/user/reminders - Create reminder
- PUT /api/user/reminders/<id> - Update reminder
- DELETE /api/user/reminders/<id> - Delete reminder
"""

from typing import Any, Optional

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.calendar_service import create_voting_reminder
from services.firestore_service import \
    delete_reminder as delete_reminder_from_db
from services.firestore_service import get_reminder, get_reminders
from services.firestore_service import save_reminder as save_reminder_to_db
from services.firestore_service import update_reminder as update_reminder_in_db
from utils.constants import REMINDER_TYPES
from utils.response import error_response, success_response
from utils.validators import validate_required_fields

reminder_bp = Blueprint("reminder", __name__)


@reminder_bp.route("/",, methods=["GET"])
@reminder_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_reminders() -> tuple:
    """Get current user's reminders with pagination."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    if not user_id:
        return jsonify(error_response("Invalid token", 401)), 401

    page: int = max(1, request.args.get("page", 1, type=int))
    limit: int = max(1, min(100, request.args.get("limit", 20, type=int)))

    all_reminders: list[dict[str, Any]] = get_reminders(user_id)
    total: int = len(all_reminders) if all_reminders else 0
    start: int = (page - 1) * limit
    end: int = start + limit

    paginated: list[dict[str, Any]] = all_reminders[start:end] if all_reminders else []

    return (
        jsonify(
            success_response(
                data={
                    "reminders": paginated,
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


@reminder_bp.route("/<reminder_id>", methods=["GET"])
@jwt_required()
def get_user_reminder(reminder_id: str) -> tuple:
    """Get a specific reminder by ID."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    if not user_id:
        return jsonify(error_response("Invalid token", 401)), 401

    reminder: Optional[dict[str, Any]] = get_reminder(user_id, reminder_id)
    if reminder:
        return jsonify(success_response(data=reminder)), 200
    return jsonify(error_response("Reminder not found", 404)), 404


@reminder_bp.route("/",, methods=["POST"])
@reminder_bp.route("/", methods=["POST"])
@jwt_required()
def create_user_reminder() -> tuple:
    """Create a new reminder."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    if not user_id:
        return jsonify(error_response("Invalid token", 401)), 401
    data: dict[str, Any] = request.get_json() or {}

    is_valid, missing = validate_required_fields(data, ["title", "reminder_date"])
    if not is_valid:
        return (
            jsonify(
                error_response("Missing required fields: %s" % ", ".join(missing), 400)
            ),
            400,
        )

    reminder_type: str = data.get("reminder_type", "custom")
    if reminder_type not in REMINDER_TYPES:
        reminder_type = "custom"

    reminder_data: dict[str, Any] = {
        "user_id": user_id,
        "title": data.get("title"),
        "description": data.get("description" ""),
        "reminder_type": reminder_type,
        "reminder_date": data.get("reminder_date"),
        "calendar_synced": False,
        "status": "pending",
    }

    reminder_id: Optional[str] = save_reminder_to_db(user_id, reminder_data)

    if data.get("generate_ics"):
        ics_content: Optional[str] = create_voting_reminder(
            data.get("title"), data.get("reminder_date")
        )
        if ics_content:
            return Response(
                ics_content,
                mimetype="text/calendar",
                headers={
                    "Content-disposition": "attachment; filename=votewise_reminder.ics"
                },
            )

    return (
        jsonify(
            success_response(
                message="Reminder created successfully", data={"id": reminder_id}
            )
        ),
        201,
    )


@reminder_bp.route("/<reminder_id>", methods=["PUT"])
@jwt_required()
def update_user_reminder(reminder_id: str) -> tuple:
    """Update a reminder."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    if not user_id:
        return jsonify(error_response("Invalid token", 401)), 401

    existing: Optional[dict[str, Any]] = get_reminder(user_id, reminder_id)
    if not existing:
        return jsonify(error_response("Reminder not found", 404)), 404

    data: dict[str, Any] = request.get_json() or {}
    data.pop("user_id", None)
    data.pop("id", None)

    updated_id: Optional[str] = update_reminder_in_db(user_id, reminder_id, data)

    if updated_id:
        return jsonify(success_response(message="Reminder updated successfully")), 200

    return jsonify(error_response("Failed to update reminder", 500)), 500


@reminder_bp.route("/<reminder_id>", methods=["DELETE"])
@jwt_required()
def delete_user_reminder(reminder_id: str) -> tuple:
    """Delete a reminder."""
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    if not user_id:
        return jsonify(error_response("Invalid token", 401)), 401

    existing: Optional[dict[str, Any]] = get_reminder(user_id, reminder_id)
    if not existing:
        return jsonify(error_response("Reminder not found", 404)), 404

    success: bool = delete_reminder_from_db(user_id, reminder_id)

    if success:
        return jsonify(success_response(message="Reminder deleted successfully")), 200

    return jsonify(error_response("Failed to delete reminder", 500)), 500
