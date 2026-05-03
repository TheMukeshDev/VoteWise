"""
Polling Guidance Routes for VoteWise AI

Admin polling guidance management endpoints:
- GET /api/admin/polling-guidance - Get all polling guidance (admin)
- GET /api/admin/polling-guidance/<id> - Get specific guidance (admin)
- POST /api/admin/polling-guidance - Create guidance (admin)
- PUT /api/admin/polling-guidance/<id> - Update guidance (admin)
- DELETE /api/admin/polling-guidance/<id> - Delete guidance (admin)
"""

from typing import Any, Optional

from flask import Blueprint, jsonify, request

from middleware.auth_middleware import require_admin
from services.polling_guidance_service import polling_guidance_service
from utils.response import error_response, success_response
from utils.validators import validate_required_fields

polling_guidance_bp = Blueprint("polling_guidance_admin", __name__)


@polling_guidance_bp.route(", ", methods=["GET"])
@polling_guidance_bp.route("/", methods=["GET"])
@require_admin
def get_polling_guidances() -> tuple:
    """Get all polling guidance with optional region filter (admin)."""
    region: Optional[str] = request.args.get("region")

    guidances: list[dict[str, Any]] = polling_guidance_service.get_all_for_admin()

    if region:
        guidances = [g for g in guidances if g.get("region") == region]

    return jsonify(success_response(data=guidances)), 200


@polling_guidance_bp.route("/<guidance_id>", methods=["GET"])
@require_admin
def get_polling_guidance(guidance_id: str) -> tuple:
    """Get a specific polling guidance by ID (admin)."""
    guidance: Optional[dict[str, Any]] = polling_guidance_service.get_by_id(guidance_id)

    if not guidance:
        return jsonify(error_response("Polling guidance not found", 404)), 404

    return jsonify(success_response(data=guidance)), 200


@polling_guidance_bp.route(", ", methods=["POST"])
@polling_guidance_bp.route("/", methods=["POST"])
@require_admin
def create_polling_guidance() -> tuple:
    """Create a new polling guidance (admin only)."""
    data: dict[str, Any] = request.get_json() or {}

    is_valid, missing = validate_required_fields(data, ["region", "title", "description"])
    if not is_valid:
        return (
            jsonify(error_response(f"Missing required fields: {', '.join(missing)}", 400)),
            400,
        )

    guidance: Optional[dict[str, Any]] = polling_guidance_service.create(
        region=data["region"],
        title=data["title"],
        description=data["description"],
        help_links=data.get("help_links"),
        is_active=data.get("is_active", True),
    )

    return (
        jsonify(success_response(message="Polling guidance created successfully", data=guidance)),
        201,
    )


@polling_guidance_bp.route("/<guidance_id>", methods=["PUT"])
@require_admin
def update_polling_guidance(guidance_id: str) -> tuple:
    """Update a polling guidance (admin only)."""
    data: dict[str, Any] = request.get_json() or {}

    guidance: Optional[dict[str, Any]] = polling_guidance_service.update(guidance_id, data)

    if not guidance:
        return jsonify(error_response("Polling guidance not found", 404)), 404

    return (
        jsonify(success_response(message="Polling guidance updated successfully", data=guidance)),
        200,
    )


@polling_guidance_bp.route("/<guidance_id>", methods=["DELETE"])
@require_admin
def delete_polling_guidance(guidance_id: str) -> tuple:
    """Delete a polling guidance (admin only)."""
    success: bool = polling_guidance_service.delete(guidance_id)

    if not success:
        return jsonify(error_response("Polling guidance not found", 404)), 404

    return (
        jsonify(success_response(message="Polling guidance deleted successfully")),
        200,
    )
