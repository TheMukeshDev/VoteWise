"""
Flask Authentication Middleware for VoteWise AI

Provides JWT-based authentication with Firebase token verification.
Handles:
- Token verification
- Role-based access control
- User session management
"""

from functools import wraps
import os
from flask import request, jsonify, g
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    verify_jwt_in_request,
    get_jwt_identity,
    get_jwt,
)
from typing import Callable, Optional, Dict, Any, List

from services.auth_service import firebase_auth_service, user_profile_service
from config import Config

ALLOWED_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").lower()

jwt_manager = JWTManager()


def init_auth_middleware(app):
    """Initialize JWT manager and configure JWT settings."""
    jwt_manager.init_app(app)

    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify(
            {"success": False, "message": "Token has expired", "error": "token_expired"}
        ), 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(
            {"success": False, "message": "Invalid token", "error": "invalid_token"}
        ), 401

    @jwt_manager.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify(
            {
                "success": False,
                "message": "Authorization required",
                "error": "authorization_required",
            }
        ), 401


def setup_auth_middleware(app):
    """Setup authentication middleware for the Flask app."""
    init_auth_middleware(app)

    @app.before_request
    def before_request_handler():
        """Process authentication before each request."""
        g.current_user = None
        g.user_role = None


def generate_tokens(user_id: str, role: str = "voter") -> Dict[str, str]:
    """
    Generate access and refresh tokens for a user.

    Args:
        user_id: Firebase user ID
        role: User role (voter/admin)

    Returns:
        Dictionary with access_token and refresh_token
    """
    additional_claims = {"role": role}

    access_token = create_access_token(
        identity={"user_id": user_id, "role": role}, additional_claims=additional_claims
    )

    refresh_token = create_refresh_token(identity={"user_id": user_id})

    return {"access_token": access_token, "refresh_token": refresh_token}


def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Firebase ID token and return claims.

    Args:
        id_token: Firebase ID token from client

    Returns:
        Decoded token claims or None
    """
    return firebase_auth_service.verify_id_token(id_token)


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user from Flask g object."""
    return getattr(g, "current_user", None)


def get_current_user_role() -> Optional[str]:
    """Get current user role from Flask g object."""
    return getattr(g, "user_role", None)


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            g.current_user = user_profile_service.get_user_profile(identity["user_id"])
            g.user_role = identity.get("role", "voter")
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify(
                {
                    "success": False,
                    "message": str(e),
                    "error": "authentication_required",
                }
            ), 401

    return decorated_function


def require_role(allowed_roles: List[str]) -> Callable:
    """
    Decorator to require specific role(s) for a route.

    Args:
        allowed_roles: List of allowed roles (e.g., ["admin"])
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                user_role = identity.get("role", "voter")

                if user_role not in allowed_roles:
                    return jsonify(
                        {
                            "success": False,
                            "message": "Insufficient permissions",
                            "error": "forbidden",
                        }
                    ), 403

                user_profile = user_profile_service.get_user_profile(
                    identity["user_id"]
                )
                g.current_user = user_profile
                g.user_role = user_role

                if user_role == "admin":
                    user_email = user_profile.get("email", "") if user_profile else ""
                    if user_email.lower() != ALLOWED_ADMIN_EMAIL.lower():
                        return jsonify(
                            {
                                "success": False,
                                "message": "Admin email not authorized",
                                "error": "forbidden",
                            }
                        ), 403

                return f(*args, **kwargs)
            except Exception as e:
                return jsonify(
                    {
                        "success": False,
                        "message": str(e),
                        "error": "authentication_required",
                    }
                ), 401

        return decorated_function

    return decorator


def require_admin(f: Callable) -> Callable:
    """Decorator to require admin role."""
    return require_role(["admin"])(f)


def require_voter(f: Callable) -> Callable:
    """Decorator to require voter role."""
    return require_role(["voter", "admin"])(f)


class AuthMiddleware:
    """Authentication middleware class."""

    def __init__(self):
        self.firebase_service = firebase_auth_service
        self.profile_service = user_profile_service

    def authenticate_firebase_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate using Firebase ID token.

        Args:
            id_token: Firebase ID token from client

        Returns:
            User profile if successful
        """
        claims = self.firebase_service.verify_id_token(id_token)
        if not claims:
            return None

        user_id = claims.get("uid")
        if not user_id:
            return None

        profile = self.profile_service.get_user_profile(user_id)

        if profile:
            self.profile_service.update_last_login(user_id)

        return profile

    def get_or_create_user(self, firebase_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get existing user or create new profile.

        Args:
            firebase_user: Firebase user data

        Returns:
            User profile
        """
        user_id = firebase_user.get("uid")
        email = firebase_user.get("email")

        profile = self.profile_service.get_user_profile(user_id)

        if not profile:
            self.profile_service.create_user_profile(
                user_id=user_id, email=email, data={"email": email}
            )
            profile = self.profile_service.get_user_profile(user_id)

        return profile

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if user has permission for an action.

        Args:
            user_id: User ID
            resource: Resource type
            action: Action (read, write, delete)

        Returns:
            True if allowed
        """
        role = self.profile_service.get_user_role(user_id)

        permissions = {
            "voter": {
                "user": ["read", "write"],
                "reminder": ["read", "write", "delete"],
                "bookmark": ["read", "write", "delete"],
                "faq": ["read"],
                "timeline": ["read"],
                "election_process": ["read"],
                "announcement": ["read"],
                "polling_guidance": ["read"],
            },
            "admin": {
                "user": ["read", "write"],
                "reminder": ["read", "write", "delete"],
                "bookmark": ["read", "write", "delete"],
                "faq": ["read", "write", "delete"],
                "timeline": ["read", "write", "delete"],
                "election_process": ["read", "write", "delete"],
                "announcement": ["read", "write", "delete"],
                "polling_guidance": ["read", "write", "delete"],
                "analytics": ["read"],
            },
        }

        return action in permissions.get(role, {}).get(resource, [])


auth_middleware = AuthMiddleware()
