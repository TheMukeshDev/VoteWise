", ", "
User Routes for VoteWise AI

User-specific endpoints:
- GET /api/user/profile - Get user profile
- PUT /api/user/profile - Update user profile
- GET /api/user/preferences - Get user preferences
- PUT /api/user/preferences - Update user preferences
", ", "

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.response import success_response, error_response
from services.firestore_service import get_user, save_user
from services.auth_service import user_profile_service
from typing import Optional, Any
from utils.constants import SUPPORTED_LANGUAGES

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile() -> tuple:
    ", ", "Get current user's profile.", ", "
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")

    user_data: Optional[dict[str, Any]] = get_user(user_id)
    if user_data:
        return jsonify(success_response(data=user_data)), 200

    profile: Optional[dict[str, Any]] = user_profile_service.get_user_profile(user_id)
    if profile:
        return jsonify(success_response(data=profile)), 200

    return jsonify(error_response("Profile not found", 404)), 404


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile() -> tuple:
    ", ", "Update current user's profile.", ", "
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    data: dict[str, Any] = request.get_json() or {}

    data.pop("role", None)
    data.pop("uid", None)

    if "language_preference" in data:
        lang: str = data["language_preference"]
        if lang not in SUPPORTED_LANGUAGES:
            return jsonify(
                error_response(
                    "Invalid language. Allowed: %s" % ", ".join(SUPPORTED_LANGUAGES),
                    400,
                )
            ), 400

    saved_id: Optional[str] = save_user(user_id, data)
    if saved_id:
        updated: Optional[dict[str, Any]] = get_user(user_id)
        return jsonify(
            success_response(message="Profile updated successfully", data=updated)
        ), 200

    return jsonify(error_response("Failed to update profile", 500)), 500


@user_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_preferences() -> tuple:
    ", ", "Get current user's preferences.", ", "
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")

    user_data: Optional[dict[str, Any]] = get_user(user_id)
    if not user_data:
        return jsonify(success_response(data={})), 200

    prefs: dict[str, Any] = {
        "language_preference": user_data.get("language_preference", "en"),
        "state": user_data.get("state", ", "),
        "city": user_data.get("city", ", "),
        "first_time_voter": user_data.get("first_time_voter", False),
        "voice_enabled": user_data.get("voice_enabled", False),
        "accessibility_mode": user_data.get("accessibility_mode", False),
    }

    return jsonify(success_response(data=prefs)), 200


@user_bp.route("/preferences", methods=["PUT"])
@jwt_required()
def update_preferences() -> tuple:
    ", ", "Update current user's preferences.", ", "
    identity: dict[str, Any] = get_jwt_identity()
    user_id: Optional[str] = identity.get("user_id")
    data: dict[str, Any] = request.get_json() or {}

    allowed_fields: list[str] = [
        "language_preference",
        "state",
        "city",
        "first_time_voter",
        "voice_enabled",
        "accessibility_mode",
    ]

    prefs: dict[str, Any] = {k: v for k, v in data.items() if k in allowed_fields}

    if (
        "language_preference" in prefs
        and prefs["language_preference"] not in SUPPORTED_LANGUAGES
    ):
        return jsonify(
            error_response(
                "Invalid language. Allowed: %s" % ", ".join(SUPPORTED_LANGUAGES), 400
            )
        ), 400

    if prefs:
        saved_id: Optional[str] = save_user(user_id, prefs)
        if not saved_id:
            return jsonify(error_response("Failed to update preferences", 500)), 500

    return jsonify(success_response(message="Preferences updated successfully")), 200


@user_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def fetch_user(user_id: str) -> tuple:
    ", ", "Get user by ID (only own profile allowed).", ", "
    identity: dict[str, Any] = get_jwt_identity()
    current_user_id: Optional[str] = identity.get("user_id")

    if user_id != current_user_id:
        return jsonify(error_response("Access denied", 403)), 403

    user_data: Optional[dict[str, Any]] = get_user(user_id)
    if user_data:
        return jsonify(success_response(data=user_data)), 200
    return jsonify(error_response("User not found", 404)), 404
