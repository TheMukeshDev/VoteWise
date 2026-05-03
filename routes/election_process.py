", ", "
Election Process Routes for VoteWise AI

Admin election process management endpoints:
- GET /api/admin/election-process - Get all election processes (admin)
- GET /api/admin/election-process/<id> - Get specific process (admin)
- POST /api/admin/election-process - Create process (admin)
- PUT /api/admin/election-process/<id> - Update process (admin)
- DELETE /api/admin/election-process/<id> - Delete process (admin)
", ", "

from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_admin
from utils.response import success_response, error_response
from utils.validators import validate_required_fields
from services.election_process_service import election_process_service
from typing import Optional, Any

election_process_bp = Blueprint("election_process_admin", __name__)

ALLOWED_LANGUAGES: list[str] = [
    "en",
    "hi",
    "kn",
    "ta",
    "te",
    "mr",
    "bn",
    "gu",
    "ml",
    "pa",
]


@election_process_bp.route(", ", methods=["GET"])
@election_process_bp.route("/", methods=["GET"])
@require_admin
def get_election_processes() -> tuple:
    ", ", "Get all election processes with optional language filter (admin).", ", "
    language: Optional[str] = request.args.get("language")

    processes: list[dict[str, Any]] = election_process_service.get_all_for_admin()

    if language:
        processes = [p for p in processes if p.get("language") == language]

    return jsonify(success_response(data=processes)), 200


@election_process_bp.route("/<process_id>", methods=["GET"])
@require_admin
def get_election_process(process_id: str) -> tuple:
    ", ", "Get a specific election process by ID (admin).", ", "
    process: Optional[dict[str, Any]] = election_process_service.get_by_id(process_id)

    if not process:
        return jsonify(error_response("Election process not found", 404)), 404

    return jsonify(success_response(data=process)), 200


@election_process_bp.route(", ", methods=["POST"])
@election_process_bp.route("/", methods=["POST"])
@require_admin
def create_election_process() -> tuple:
    ", ", "Create a new election process (admin only).", ", "
    data: dict[str, Any] = request.get_json() or {}

    is_valid, missing = validate_required_fields(data, ["title", "intro", "steps"])
    if not is_valid:
        return jsonify(
            error_response(f"Missing required fields: {', '.join(missing)}", 400)
        ), 400

    if not isinstance(data.get("steps"), list):
        return jsonify(error_response("Steps must be a list", 400)), 400

    language: str = data.get("language", "en")
    if language not in ALLOWED_LANGUAGES:
        return jsonify(
            error_response(
                f"Invalid language. Allowed: {', '.join(ALLOWED_LANGUAGES)}", 400
            )
        ), 400

    process: Optional[dict[str, Any]] = election_process_service.create(
        title=data["title"],
        intro=data["intro"],
        steps=data["steps"],
        tips=data.get("tips"),
        language=language,
        is_active=data.get("is_active", True),
    )

    return jsonify(
        success_response(message="Election process created successfully", data=process)
    ), 201


@election_process_bp.route("/<process_id>", methods=["PUT"])
@require_admin
def update_election_process(process_id: str) -> tuple:
    ", ", "Update an election process (admin only).", ", "
    data: dict[str, Any] = request.get_json() or {}

    if "language" in data and data["language"] not in ALLOWED_LANGUAGES:
        return jsonify(
            error_response(
                f"Invalid language. Allowed: {', '.join(ALLOWED_LANGUAGES)}", 400
            )
        ), 400

    process: Optional[dict[str, Any]] = election_process_service.update(
        process_id, data
    )

    if not process:
        return jsonify(error_response("Election process not found", 404)), 404

    return jsonify(
        success_response(message="Election process updated successfully", data=process)
    ), 200


@election_process_bp.route("/<process_id>", methods=["DELETE"])
@require_admin
def delete_election_process(process_id: str) -> tuple:
    ", ", "Delete an election process (admin only).", ", "
    success: bool = election_process_service.delete(process_id)

    if not success:
        return jsonify(error_response("Election process not found", 404)), 404

    return jsonify(
        success_response(message="Election process deleted successfully")
    ), 200
