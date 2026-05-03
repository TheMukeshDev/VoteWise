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

import logging
import secrets

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from config import Config
from middleware.auth_middleware import (check_rate_limit, generate_tokens,
                                        rate_limit_key_func,
                                        verify_firebase_token)
from services.auth_service import user_profile_service
from utils.response import error_response, success_response

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login with Firebase ID token. Rate limited: 10 attempts per minute."""
    rate_key = f"user_login:{rate_limit_key_func()}"
    if not check_rate_limit(rate_key, max_requests=10, window_seconds=60):
        return jsonify(error_response("Too many attempts. Try again later.", 429)), 429

    try:
        data = request.get_json(silent=True) or {}
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
                email=email or ", ",
                data={
                    "email": email,
                    "full_name": decoded_token.get("name"),
                    "role": "voter",
                },
            )
            profile = user_profile_service.get_user_profile(user_id)

        user_profile_service.update_last_login(user_id)

        role = profile.get("role", "voter") if profile else "voter"
        tokens = generate_tokens(user_id, role)

        return (
            jsonify(
                success_response(
                    message="Login successful",
                    data={
                        "user": profile,
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"],
                    },
                )
            ),
            200,
        )

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Login error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration with Firebase ID token. Rate limited: 5 attempts per minute."""
    rate_key = f"register:{rate_limit_key_func()}"
    if not check_rate_limit(rate_key, max_requests=5, window_seconds=60):
        return jsonify(error_response("Too many attempts. Try again later.", 429)), 429

    try:
        data = request.get_json(silent=True) or {}
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
            "full_name", decoded_token.get("name")
        )

        user_profile_service.create_user_profile(
            user_id=user_id, email=email or ", ", data=profile_data
        )
        profile = user_profile_service.get_user_profile(user_id)

        return (
            jsonify(
                success_response(
                    message="Registration successful", data={"user": profile}
                )
            ),
            201,
        )

    except ValueError as e:
        return jsonify(error_response(str(e), 400)), 400
    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Registration error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/google-signin", methods=["POST"])
def google_signin():
    """Google Sign-In authentication. Rate limited: 10 attempts per minute."""
    rate_key = f"google_signin:{rate_limit_key_func()}"
    if not check_rate_limit(rate_key, max_requests=10, window_seconds=60):
        return jsonify(error_response("Too many attempts. Try again later.", 429)), 429

    try:
        data = request.get_json(silent=True) or {}
        id_token = data.get("id_token")
        if not id_token:
            return jsonify(error_response("ID token is required", 400)), 400

        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify(error_response("Invalid or expired token", 401)), 401

        user_id = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name")

        profile = user_profile_service.get_user_profile(user_id)
        if not profile:
            user_profile_service.create_user_profile(
                user_id=user_id,
                email=email or "",
                data={"email": email, "full_name": name, "role": "voter"},
            )
            profile = user_profile_service.get_user_profile(user_id)
            user_profile_service.update_last_login(user_id)

        role = profile.get("role", "voter") if profile else "voter"
        tokens = generate_tokens(user_id, role)

        return (
            jsonify(
                success_response(
                    message="Google Sign-In successful",
                    data={
                        "user": profile,
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"],
                    },
                )
            ),
            200,
        )

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Google sign-in error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user details. Requires valid JWT token."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        if not user_id:
            return jsonify(error_response("Invalid token", 401)), 401

        profile = user_profile_service.get_user_profile(user_id)
        if profile:
            return jsonify(success_response(data=profile)), 200

        return jsonify(error_response("User not found", 404)), 404

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Get current user error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user profile."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        if not user_id:
            return jsonify(error_response("Invalid token", 401)), 401

        data = request.get_json(silent=True) or {}
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

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Update profile error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token using refresh token."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        if not user_id:
            return jsonify(error_response("Invalid token", 401)), 401

        role = user_profile_service.get_user_role(user_id) or "voter"
        tokens = generate_tokens(user_id, role)

        return (
            jsonify(success_response(data={"access_token": tokens["access_token"]})),
            200,
        )

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Token refresh error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/role-check", methods=["GET"])
@jwt_required()
def check_role():
    """Check current user role. Requires valid JWT token."""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("user_id")
        if not user_id:
            return jsonify(error_response("Invalid token", 401)), 401

        role = user_profile_service.get_user_role(user_id)
        return jsonify(success_response(data={"user_id": user_id, "role": role})), 200

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Role check error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """Admin login endpoint. Rate limited: 5 attempts per minute."""
    rate_key = f"admin_login:{rate_limit_key_func()}"
    if not check_rate_limit(rate_key, max_requests=5, window_seconds=60):
        logger.warning(
            "Rate limit exceeded for admin login from %s", request.remote_addr
        )
        return jsonify(error_response("Too many attempts. Try again later.", 429)), 429

    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        admin_email = Config.ADMIN_EMAIL
        admin_password = Config.ADMIN_PASSWORD

        if not admin_email or not admin_password:
            return jsonify(error_response("Admin not configured", 500)), 500

        if not secrets.compare_digest(
            email.encode("utf-8"), admin_email.lower().encode("utf-8")
        ):
            logger.warning("Failed admin login attempt for email: %s", email)
            return jsonify(error_response("Invalid admin credentials", 401)), 401

        if (
            not secrets.compare_digest(
                password.encode("utf-8"), admin_password.encode("utf-8")
            )
            or not password
        ):
            logger.warning("Failed admin login attempt for email: %s", email)
            return jsonify(error_response("Invalid admin credentials", 401)), 401

        tokens = generate_tokens("admin_user", "admin")
        logger.info("Admin login successful: %s", email)

        return (
            jsonify(
                success_response(
                    message="Admin login successful",
                    data={
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"],
                        "role": "admin",
                        "email": admin_email,
                    },
                )
            ),
            200,
        )

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Admin login error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@auth_bp.route("/verify", methods=["POST"])
def verify_token():
    """Verify Firebase ID token and upsert user profile."""
    try:
        data = request.get_json(silent=True) or {}
        id_token = data.get("id_token")
        form_name = data.get("name")

        if not id_token:
            return jsonify(error_response("ID token is required", 400)), 400

        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify(error_response("Invalid or expired token", 401)), 401

        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        if not uid or not email:
            return jsonify(error_response("Invalid token claims", 401)), 401

        display_name = decoded_token.get("name")
        photo_url = decoded_token.get("picture")
        email_verified = decoded_token.get("email_verified", False)
        provider_id = decoded_token.get("provider_id", "firebase")

        name = form_name or display_name
        if not name:
            name = email.split("@")[0]

        profile = user_profile_service.upsert_user_profile(
            firebase_uid=uid,
            email=email,
            name=name,
            photo_url=photo_url,
            email_verified=email_verified,
            provider_id=provider_id,
        )

        if not profile:
            return jsonify(error_response("Failed to create/update profile", 500)), 500

        role = profile.get("role", "user")
        tokens = generate_tokens(uid, role)

        logger.info("User verified: uid=%s, email=%s", uid, email)

        clean_user = {
            "uid": profile.get("firebase_uid"),
            "email": profile.get("email"),
            "name": profile.get("name"),
            "photo_url": profile.get("photo_url"),
            "role": profile.get("role"),
            "email_verified": profile.get("email_verified"),
            "created_at": profile.get("created_at"),
            "last_login_at": profile.get("last_login_at"),
        }

        return (
            jsonify(
                success_response(
                    message="Verification successful",
                    data={
                        "user": clean_user,
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"],
                    },
                )
            ),
            200,
        )

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Verify token error")
        return jsonify(error_response("An unexpected error occurred", 500)), 500
