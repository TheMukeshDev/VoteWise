"""
Timeline Admin Routes for VoteWise AI

Admin timeline management endpoints:
- GET /api/admin/timelines - Get all timelines (admin)
- GET /api/admin/timelines/<id> - Get specific timeline (admin)
- POST /api/admin/timelines - Create timeline (admin)
- PUT /api/admin/timelines/<id> - Update timeline (admin)
- DELETE /api/admin/timelines/<id> - Delete timeline (admin)
"""

from typing import Any, Optional

from flask import Blueprint, jsonify, request

from middleware.auth_middleware import require_admin
from services.timeline_service import timeline_service
from utils.response import error_response, success_response
from utils.validators import validate_required_fields

timeline_admin_bp = Blueprint("timeline_admin", __name__)

ALLOWED_ELECTION_TYPES: list[str] = [
    "general",
    "state",
    "municipal",
    "panchayat",
    "by-election",
]
ALLOWED_STATUSES: list[str] = ["upcoming", "ongoing", "completed", "cancelled"]


@timeline_admin_bp.route(", ", methods=["GET"])
@timeline_admin_bp.route("/", methods=["GET"])
@require_admin
def get_timelines() -> tuple:
    """Get all timelines with optional filters (admin)."""
    election_type: Optional[str] = request.args.get("election_type")
    status: Optional[str] = request.args.get("status")

    timelines = timeline_service.get_all_for_admin()

    if election_type:
        timelines = [t for t in timelines if t.get("election_type") == election_type]
    if status:
        timelines = [t for t in timelines if t.get("status") == status]

    return jsonify(success_response(data=timelines)), 200


@timeline_admin_bp.route("/<timeline_id>", methods=["GET"])
@require_admin
def get_timeline(timeline_id: str) -> tuple:
    """Get a specific timeline by ID (admin)."""
    timeline: Optional[dict[str, Any]] = timeline_service.get_by_id(timeline_id)

    if not timeline:
        return jsonify(error_response("Timeline not found", 404)), 404

    return jsonify(success_response(data=timeline)), 200


@timeline_admin_bp.route(", ", methods=["POST"])
@timeline_admin_bp.route("/", methods=["POST"])
@require_admin
def create_timeline() -> tuple:
    """Create a new timeline (admin only)."""
    data: dict[str, Any] = request.get_json() or {}

    is_valid, missing = validate_required_fields(data, ["election_type", "region", "polling_date"])
    if not is_valid:
        return (
            jsonify(error_response(f"Missing required fields: {', '.join(missing)}", 400)),
            400,
        )

    election_type: str = data.get("election_type")
    if election_type not in ALLOWED_ELECTION_TYPES:
        return (
            jsonify(
                error_response(
                    f"Invalid election_type. Allowed: {', '.join(ALLOWED_ELECTION_TYPES)}",
                    400,
                )
            ),
            400,
        )

    status: str = data.get("status", "upcoming")
    if status not in ALLOWED_STATUSES:
        return (
            jsonify(error_response(f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}", 400)),
            400,
        )

    timeline: Optional[dict[str, Any]] = timeline_service.create(
        election_type=election_type,
        region=data["region"],
        polling_date=data["polling_date"],
        registration_deadline=data.get("registration_deadline"),
        result_date=data.get("result_date"),
        status=status,
    )

    return (
        jsonify(success_response(message="Timeline created successfully", data=timeline)),
        201,
    )


@timeline_admin_bp.route("/<timeline_id>", methods=["PUT"])
@require_admin
def update_timeline(timeline_id: str) -> tuple:
    """Update a timeline (admin only)."""
    data: dict[str, Any] = request.get_json() or {}

    if "election_type" in data and data["election_type"] not in ALLOWED_ELECTION_TYPES:
        return (
            jsonify(
                error_response(
                    f"Invalid election_type. Allowed: {', '.join(ALLOWED_ELECTION_TYPES)}",
                    400,
                )
            ),
            400,
        )

    if "status" in data and data["status"] not in ALLOWED_STATUSES:
        return (
            jsonify(error_response(f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}", 400)),
            400,
        )

    timeline: Optional[dict[str, Any]] = timeline_service.update(timeline_id, data)

    if not timeline:
        return jsonify(error_response("Timeline not found", 404)), 404

    return (
        jsonify(success_response(message="Timeline updated successfully", data=timeline)),
        200,
    )


@timeline_admin_bp.route("/<timeline_id>", methods=["DELETE"])
@require_admin
def delete_timeline(timeline_id: str) -> tuple:
    """Delete a timeline (admin only)."""
    success: bool = timeline_service.delete(timeline_id)

    if not success:
        return jsonify(error_response("Timeline not found", 404)), 404

    return jsonify(success_response(message="Timeline deleted successfully")), 200
