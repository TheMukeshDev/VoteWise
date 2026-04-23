"""
Authentication Routes for VoteWise AI

Handles user authentication:
- POST /api/auth/login (Firebase token)
- POST /api/auth/register (Firebase token)
- POST /api/auth/google-signin
- GET /api/auth/me
- PUT /api/auth/profile

Uses Firebase Authentication with JWT tokens.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from utils.response import success_response, error_response
from utils.validators import validate_email
from services.auth_service import firebase_auth_service, user_profile_service
from middleware.auth_middleware import generate_tokens, verify_firebase_token
from config import Config

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login with Firebase ID token.
    Expected JSON: {"id_token": "firebase_id_token"}
    """
    try:
        data = request.get_json() or {}
        id_token = data.get("id_token")

        if not id_token:
            return jsonify(error_response("ID token is required", 400)), 400

        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify(error_response("Invalid token", 401)), 401

        user_id = decoded_token.get("uid")
        email = decoded_token.get("email")

        if not user_id:
            return jsonify(error_response("Invalid token claims", 401)), 401

        profile = user_profile_service.get_user_profile(user_id)

        if not profile:
            user_profile_service.create_user_profile(
                user_id=user_id,
                email=email,
                data={
                    "email": email,
                    "full_name": decoded_token.get("name", ""),
                    "role": "voter",
                },
            )
            profile = user_profile_service.get_user_profile(user_id)

        user_profile_service.update_last_login(user_id)

        role = profile.get("role", "voter") if profile else "voter"
        tokens = generate_tokens(user_id, role)

        return jsonify(
            success_response(
                message="Login successful",
                data={
                    "user": profile,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                },
            )
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    User registration with Firebase ID token.
    Expected JSON: {"id_token": "firebase_id_token", "profile": {...}}
    """
    try:
        data = request.get_json() or {}
        id_token = data.get("id_token")

        if not id_token:
            return jsonify(error_response("ID token is required", 400)), 400

        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify(error_response("Invalid token", 401)), 401

        user_id = decoded_token.get("uid")
        email = decoded_token.get("email")

        if not user_id:
            return jsonify(error_response("Invalid token claims", 401)), 401

        existing = user_profile_service.get_user_profile(user_id)
        if existing:
            return jsonify(error_response("User already exists", 400)), 400

        profile_data = data.get("profile", {})
        profile_data["email"] = email
        profile_data["full_name"] = profile_data.get(
            "full_name", decoded_token.get("name", "")
        )

        user_profile_service.create_user_profile(
            user_id=user_id, email=email, data=profile_data
        )

        profile = user_profile_service.get_user_profile(user_id)

        return jsonify(
            success_response(message="Registration successful", data={"user": profile})
        ), 201

    except ValueError as e:
        return jsonify(error_response(str(e), 400)), 400
    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/google-signin", methods=["POST"])
def google_signin():
    """
    Google Sign-In authentication.
    Expected JSON: {"id_token": "google_id_token"}
    """
    try:
        data = request.get_json() or {}
        id_token = data.get("id_token")

        if not id_token:
            return jsonify(error_response("ID token is required", 400)), 400

        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify(error_response("Invalid or expired token", 401)), 401

        user_id = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name", "")

        profile = user_profile_service.get_user_profile(user_id)

        if not profile:
            user_profile_service.create_user_profile(
                user_id=user_id,
                email=email,
                data={"email": email, "full_name": name, "role": "voter"},
            )
            profile = user_profile_service.get_user_profile(user_id)
            user_profile_service.update_last_login(user_id)

        role = profile.get("role", "voter") if profile else "voter"
        tokens = generate_tokens(user_id, role)

        return jsonify(
            success_response(
                message="Google Sign-In successful",
                data={
                    "user": profile,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                },
            )
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current user details.
    Requires valid JWT token.
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        profile = user_profile_service.get_user_profile(user_id)

        if profile:
            return jsonify(success_response(data=profile)), 200

        return jsonify(error_response("User not found", 404)), 404

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update current user profile.
    Expected JSON: {"full_name": "...", "state": "...", "city": "...", ...}
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        data = request.get_json() or {}

        allowed_fields = [
            "full_name",
            "language_preference",
            "state",
            "city",
            "first_time_voter",
            "profile_completed",
        ]

        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return jsonify(error_response("No valid fields to update", 400)), 400

        success = user_profile_service.update_user_profile(user_id, update_data)

        if success:
            profile = user_profile_service.get_user_profile(user_id)
            return jsonify(success_response(message="Profile updated", data=profile))

        return jsonify(error_response("Failed to update profile", 500)), 500

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token using refresh token.
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        role = user_profile_service.get_user_role(user_id) or "voter"
        tokens = generate_tokens(user_id, role)

        return jsonify(
            success_response(data={"access_token": tokens["access_token"]})
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/role-check", methods=["GET"])
@jwt_required()
def check_role():
    """
    Check current user role.
    Requires valid JWT token.
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")

        role = user_profile_service.get_user_role(user_id)

        return jsonify(success_response(data={"user_id": user_id, "role": role})), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """
    Admin login endpoint.
    Expected JSON: {"email": "...", "password": "..."}

    Validates against ADMIN_EMAIL and ADMIN_PASSWORD from environment.
    """
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        admin_email = Config.ADMIN_EMAIL
        admin_password = Config.ADMIN_PASSWORD

        if not admin_email or not admin_password:
            return jsonify(error_response("Admin not configured", 500)), 500

        if email != admin_email.lower():
            return jsonify(error_response("Invalid admin credentials", 401)), 401

        if password != admin_password:
            return jsonify(error_response("Invalid admin credentials", 401)), 401

        tokens = generate_tokens("admin_user", "admin")

        return jsonify(
            success_response(
                message="Admin login successful",
                data={
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "role": "admin",
                    "email": admin_email,
                },
            )
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
