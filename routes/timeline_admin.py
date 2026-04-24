"""
Timeline Admin Routes for VoteWise AI

Admin timeline management endpoints:
- GET /api/admin/timelines - Get all timelines (admin)
- GET /api/admin/timelines/<id> - Get specific timeline (admin)
- POST /api/admin/timelines - Create timeline (admin)
- PUT /api/admin/timelines/<id> - Update timeline (admin)
- DELETE /api/admin/timelines/<id> - Delete timeline (admin)
"""

from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_admin
from utils.response import success_response, error_response
from utils.validators import validate_required_fields
from services.timeline_service import timeline_service

timeline_admin_bp = Blueprint("timeline_admin", __name__)

ALLOWED_ELECTION_TYPES = ["general", "state", "municipal", "panchayat", "by-election"]
ALLOWED_STATUSES = ["upcoming", "ongoing", "completed", "cancelled"]


@timeline_admin_bp.route("", methods=["GET"])
@timeline_admin_bp.route("/", methods=["GET"])
@require_admin
def get_timelines():
    """Get all timelines (admin)."""
    try:
        election_type = request.args.get("election_type")
        status = request.args.get("status")

        timelines = timeline_service.get_all_for_admin()

        if election_type:
            timelines = [
                t for t in timelines if t.get("election_type") == election_type
            ]
        if status:
            timelines = [t for t in timelines if t.get("status") == status]

        return jsonify(success_response(data=timelines)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_admin_bp.route("/<timeline_id>", methods=["GET"])
@require_admin
def get_timeline(timeline_id):
    """Get a specific timeline (admin)."""
    try:
        timeline = timeline_service.get_by_id(timeline_id)

        if not timeline:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(success_response(data=timeline)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_admin_bp.route("", methods=["POST"])
@timeline_admin_bp.route("/", methods=["POST"])
@require_admin
def create_timeline():
    """Create a new timeline (admin only)."""
    try:
        data = request.get_json() or {}

        is_valid, missing = validate_required_fields(
            data, ["election_type", "region", "polling_date"]
        )
        if not is_valid:
            return jsonify(
                error_response(f"Missing required fields: {', '.join(missing)}", 400)
            ), 400

        election_type = data.get("election_type")
        if election_type not in ALLOWED_ELECTION_TYPES:
            return jsonify(
                error_response(
                    f"Invalid election_type. Allowed: {', '.join(ALLOWED_ELECTION_TYPES)}",
                    400,
                )
            ), 400

        status = data.get("status", "upcoming")
        if status not in ALLOWED_STATUSES:
            return jsonify(
                error_response(
                    f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}", 400
                )
            ), 400

        timeline = timeline_service.create(
            election_type=election_type,
            region=data["region"],
            polling_date=data["polling_date"],
            registration_deadline=data.get("registration_deadline"),
            result_date=data.get("result_date"),
            status=status,
        )

        return jsonify(
            success_response(message="Timeline created successfully", data=timeline)
        ), 201

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_admin_bp.route("/<timeline_id>", methods=["PUT"])
@require_admin
def update_timeline(timeline_id):
    """Update a timeline (admin only)."""
    try:
        data = request.get_json() or {}

        if (
            "election_type" in data
            and data["election_type"] not in ALLOWED_ELECTION_TYPES
        ):
            return jsonify(
                error_response(
                    f"Invalid election_type. Allowed: {', '.join(ALLOWED_ELECTION_TYPES)}",
                    400,
                )
            ), 400

        if "status" in data and data["status"] not in ALLOWED_STATUSES:
            return jsonify(
                error_response(
                    f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}", 400
                )
            ), 400

        timeline = timeline_service.update(timeline_id, data)

        if not timeline:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(
            success_response(message="Timeline updated successfully", data=timeline)
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_admin_bp.route("/<timeline_id>", methods=["DELETE"])
@require_admin
def delete_timeline(timeline_id):
    """Delete a timeline (admin only)."""
    try:
        success = timeline_service.delete(timeline_id)

        if not success:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(success_response(message="Timeline deleted successfully")), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
