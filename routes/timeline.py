"""
Timeline Routes for VoteWise AI

Public and admin timeline management endpoints:
- GET /api/timeline - Get all timeline events
- GET /api/timeline/<id> - Get specific event
- POST /api/admin/timeline - Create timeline event (admin)
- PUT /api/admin/timeline/<id> - Update event (admin)
- DELETE /api/admin/timeline/<id> - Delete event (admin)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middleware.auth_middleware import require_admin
from utils.response import success_response, error_response
from utils.validators import validate_required_fields
from services.timeline_service import TimelineService

timeline_bp = Blueprint("timeline", __name__)
timeline_service = TimelineService()


@timeline_bp.route("", methods=["GET"])
@timeline_bp.route("/", methods=["GET"])
def get_timelines():
    """Get all timeline events (public)."""
    try:
        election_type = request.args.get("election_type")
        status = request.args.get("status")

        timelines = timeline_service.get_all(election_type=election_type, status=status)

        return jsonify(success_response(data=timelines)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_bp.route("/<timeline_id>", methods=["GET"])
def get_timeline(timeline_id):
    """Get a specific timeline event (public)."""
    try:
        timeline = timeline_service.get_by_id(timeline_id)

        if not timeline:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(success_response(data=timeline)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_bp.route("", methods=["POST"])
@timeline_bp.route("/", methods=["POST"])
@require_admin
def create_timeline():
    """Create a new timeline event (admin only)."""
    try:
        data = request.get_json() or {}

        is_valid, missing = validate_required_fields(
            data, ["title", "date", "event_type"]
        )
        if not is_valid:
            return jsonify(
                error_response(f"Missing required fields: {', '.join(missing)}", 400)
            ), 400

        timeline = timeline_service.create(
            title=data["title"],
            date=data["date"],
            event_type=data["event_type"],
            description=data.get("description", ""),
            status=data.get("status", "upcoming"),
        )

        return jsonify(
            success_response(message="Timeline created successfully", data=timeline)
        ), 201

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_bp.route("/<timeline_id>", methods=["PUT"])
@require_admin
def update_timeline(timeline_id):
    """Update a timeline event (admin only)."""
    try:
        data = request.get_json() or {}

        timeline = timeline_service.update(timeline_id, data)

        if not timeline:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(
            success_response(message="Timeline updated successfully", data=timeline)
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_bp.route("/<timeline_id>", methods=["DELETE"])
@require_admin
def delete_timeline(timeline_id):
    """Delete a timeline event (admin only)."""
    try:
        success = timeline_service.delete(timeline_id)

        if not success:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(success_response(message="Timeline deleted successfully")), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
