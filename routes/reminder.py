"""
User Reminder Routes for VoteWise AI

User reminder endpoints:
- GET /api/user/reminders - Get user's reminders
- POST /api/user/reminders - Create reminder
- PUT /api/user/reminders/<id> - Update reminder
- DELETE /api/user/reminders/<id> - Delete reminder
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.response import success_response, error_response
from utils.validators import validate_required_fields
from services.firestore_service import (
    get_reminders,
    get_reminder,
    save_reminder as save_reminder_to_db,
    update_reminder as update_reminder_in_db,
    delete_reminder as delete_reminder_from_db,
)
from services.calendar_service import create_voting_reminder

reminder_bp = Blueprint("reminder", __name__)

ALLOWED_REMINDER_TYPES = ["voting", "registration", "deadline", "event", "custom"]


@reminder_bp.route("", methods=["GET"])
@reminder_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_reminders():
    """Get current user's reminders with pagination."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        # Pagination
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        page = max(1, page)
        limit = max(1, min(100, limit))

        all_reminders = get_reminders(user_id)
        total = len(all_reminders) if all_reminders else 0
        start = (page - 1) * limit
        end = start + limit

        paginated = all_reminders[start:end] if all_reminders else []

        return jsonify(
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
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@reminder_bp.route("/<reminder_id>", methods=["GET"])
@jwt_required()
def get_user_reminder(reminder_id):
    """Get a specific reminder."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        reminder = get_reminder(user_id, reminder_id)
        if reminder:
            return jsonify(success_response(data=reminder)), 200
        return jsonify(error_response("Reminder not found", 404)), 404

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@reminder_bp.route("", methods=["POST"])
@reminder_bp.route("/", methods=["POST"])
@jwt_required()
def create_user_reminder():
    """Create a new reminder."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        data = request.get_json() or {}

        is_valid, missing = validate_required_fields(data, ["title", "reminder_date"])
        if not is_valid:
            return jsonify(
                error_response(f"Missing required fields: {', '.join(missing)}", 400)
            ), 400

        reminder_type = data.get("reminder_type", "custom")
        if reminder_type not in ALLOWED_REMINDER_TYPES:
            reminder_type = "custom"

        reminder_data = {
            "user_id": user_id,
            "title": data.get("title"),
            "description": data.get("description", ""),
            "reminder_type": reminder_type,
            "reminder_date": data.get("reminder_date"),
            "calendar_synced": False,
            "status": "pending",
        }

        reminder_id = save_reminder_to_db(user_id, reminder_data)

        if data.get("generate_ics"):
            ics_content = create_voting_reminder(
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

        return jsonify(
            success_response(
                message="Reminder created successfully", data={"id": reminder_id}
            )
        ), 201

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@reminder_bp.route("/<reminder_id>", methods=["PUT"])
@jwt_required()
def update_user_reminder(reminder_id):
    """Update a reminder."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        existing = get_reminder(user_id, reminder_id)
        if not existing:
            return jsonify(error_response("Reminder not found", 404)), 404

        data = request.get_json() or {}
        data.pop("user_id", None)
        data.pop("id", None)

        updated_id = update_reminder_in_db(user_id, reminder_id, data)

        if updated_id:
            return jsonify(
                success_response(message="Reminder updated successfully")
            ), 200

        return jsonify(error_response("Failed to update reminder", 500)), 500

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@reminder_bp.route("/<reminder_id>", methods=["DELETE"])
@jwt_required()
def delete_user_reminder(reminder_id):
    """Delete a reminder."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        existing = get_reminder(user_id, reminder_id)
        if not existing:
            return jsonify(error_response("Reminder not found", 404)), 404

        success = delete_reminder_from_db(user_id, reminder_id)

        if success:
            return jsonify(
                success_response(message="Reminder deleted successfully")
            ), 200

        return jsonify(error_response("Failed to delete reminder", 500)), 500

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
