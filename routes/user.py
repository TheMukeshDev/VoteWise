"""
User Routes for VoteWise AI

User-specific endpoints:
- GET /api/user/profile - Get user profile
- PUT /api/user/profile - Update user profile
- GET /api/user/preferences - Get user preferences
- PUT /api/user/preferences - Update user preferences
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.response import success_response, error_response
from services.firestore_service import get_user, save_user
from services.auth_service import user_profile_service

user_bp = Blueprint("user", __name__)

ALLOWED_LANGUAGES = ["en", "hi", "kn", "ta", "te", "mr", "bn", "gu", "ml", "pa"]


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user's profile."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        user_data = get_user(user_id)
        if user_data:
            return jsonify(success_response(data=user_data)), 200

        profile = user_profile_service.get_user_profile(user_id)
        if profile:
            return jsonify(success_response(data=profile)), 200

        return jsonify(error_response("Profile not found", 404)), 404

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user's profile."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        data = request.get_json() or {}

        data.pop("role", None)
        data.pop("uid", None)

        if "language_preference" in data:
            lang = data["language_preference"]
            if lang not in ALLOWED_LANGUAGES:
                return jsonify(
                    error_response(
                        f"Invalid language. Allowed: {', '.join(ALLOWED_LANGUAGES)}",
                        400,
                    )
                ), 400

        saved_id = save_user(user_id, data)
        if saved_id:
            updated = get_user(user_id)
            return jsonify(
                success_response(message="Profile updated successfully", data=updated)
            ), 200

        return jsonify(error_response("Failed to update profile", 500)), 500

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@user_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_preferences():
    """Get current user's preferences."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        user_data = get_user(user_id)
        if not user_data:
            return jsonify(success_response(data={})), 200

        prefs = {
            "language_preference": user_data.get("language_preference", "en"),
            "state": user_data.get("state", ""),
            "city": user_data.get("city", ""),
            "first_time_voter": user_data.get("first_time_voter", False),
            "voice_enabled": user_data.get("voice_enabled", False),
            "accessibility_mode": user_data.get("accessibility_mode", False),
        }

        return jsonify(success_response(data=prefs)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@user_bp.route("/preferences", methods=["PUT"])
@jwt_required()
def update_preferences():
    """Update current user's preferences."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        data = request.get_json() or {}

        allowed_fields = [
            "language_preference",
            "state",
            "city",
            "first_time_voter",
            "voice_enabled",
            "accessibility_mode",
        ]

        prefs = {k: v for k, v in data.items() if k in allowed_fields}

        if (
            "language_preference" in prefs
            and prefs["language_preference"] not in ALLOWED_LANGUAGES
        ):
            return jsonify(
                error_response(
                    f"Invalid language. Allowed: {', '.join(ALLOWED_LANGUAGES)}", 400
                )
            ), 400

        if prefs:
            saved_id = save_user(user_id, prefs)
            if not saved_id:
                return jsonify(error_response("Failed to update preferences", 500)), 500

        return jsonify(
            success_response(message="Preferences updated successfully")
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@user_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def fetch_user(user_id):
    """Get user by ID (only own profile allowed)."""
    try:
        identity = get_jwt_identity()
        current_user_id = identity.get("user_id")

        if user_id != current_user_id:
            return jsonify(error_response("Access denied", 403)), 403

        user_data = get_user(user_id)
        if user_data:
            return jsonify(success_response(data=user_data)), 200
        return jsonify(error_response("User not found", 404)), 404

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
