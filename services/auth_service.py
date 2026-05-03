"""
Firebase Authentication Service for VoteWise AI

Handles:
- Email/password authentication
- Google Sign-In
- User session management
- Role-based access control
"""

import datetime
import logging
from typing import Any, Optional

import firebase_admin
from firebase_admin import auth, credentials

from config import Config
from services.firestore_service import get_firestore_client, get_user

logger = logging.getLogger(__name__)


def _server_timestamp() -> datetime.datetime:
    """Get server timestamp for Firestore."""
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


_firebase_initialized: bool = False


def _ensure_firebase_initialized() -> bool:
    """Ensure Firebase is initialized exactly once."""
    global _firebase_initialized
    if _firebase_initialized:
        return True

    if not firebase_admin._apps:
        firebase_json = Config.FIREBASE_ADMIN_JSON
        if firebase_json:
            try:
                cred = credentials.Certificate(firebase_json)
                firebase_admin.initialize_app(
                    cred, {"projectId": Config.FIREBASE_PROJECT_ID}
                )
            except (ValueError, RuntimeError) as e:
                logger.warning("Firebase initialization warning: %s", e)
                try:
                    firebase_admin.initialize_app()
                except (ValueError, RuntimeError) as e2:
                    logger.warning("Firebase init failed: %s", e2)
                    return False
        else:
            try:
                firebase_admin.initialize_app()
            except (ValueError, RuntimeError) as e:
                logger.warning("Firebase initialization warning: %s", e)

    _firebase_initialized = True
    return _firebase_initialized


class FirebaseAuthService:
    """Service for handling Firebase Authentication operations."""

    def __init__(self) -> None:
        _ensure_firebase_initialized()

    @property
    def db(self):
        """Get Firestore client."""
        return get_firestore_client()

    def verify_id_token(self, id_token: str) -> Optional[dict[str, Any]]:
        """Verify Firebase ID token and return claims."""
        try:
            decoded_token: dict[str, Any] = auth.verify_id_token(id_token)
            return decoded_token
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, ValueError) as e:
            logger.error("Token verification failed: %s", e)
            return None

    def create_custom_token(
        self, user_id: str, additional_claims: Optional[dict] = None
    ) -> Optional[str]:
        """Create custom JWT token for user."""
        try:
            custom_token = auth.create_custom_token(user_id, additional_claims or {})
            return (
                custom_token.decode("utf-8")
                if isinstance(custom_token, bytes)
                else custom_token
            )
        except (auth.UidAlreadyExistsError, ValueError):
            return None

    def get_user(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get user from Firebase Auth."""
        try:
            user = auth.get_user(user_id)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled,
                "email_verified": user.email_verified,
                "provider_data": [
                    {"provider_id": p.provider_id, "uid": p.uid}
                    for p in user.provider_data
                ],
            }
        except auth.UserNotFoundError:
            return None
        except (auth.FirebaseError, ValueError):
            return None

    def create_user(
        self, email: str, password: str, display_name: Optional[str] = None
    ) -> Optional[dict[str, Any]]:
        """Create new user with email/password."""
        try:
            user = auth.create_user(
                email=email, password=password, display_name=display_name
            )
            return {"uid": user.uid, "email": user.email}
        except (
            auth.EmailAlreadyExistsError,
            auth.UidAlreadyExistsError,
            ValueError,
        ) as e:
            raise ValueError(str(e))

    def update_user(self, user_id: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Update user information."""
        try:
            user = auth.update_user(user_id, **kwargs)
            return {"uid": user.uid, "email": user.email}
        except (auth.FirebaseError, ValueError):
            return None

    def delete_user(self, user_id: str) -> bool:
        """Delete user from Firebase Auth."""
        try:
            auth.delete_user(user_id)
            return True
        except (auth.FirebaseError, ValueError):
            return False

    def set_custom_user_claims(
        self, user_id: str, claims: dict[str, Any]
    ) -> Optional[bool]:
        """Set custom claims for user (e.g., role)."""
        try:
            auth.set_custom_user_claims(user_id, claims)
            return True
        except (auth.FirebaseError, ValueError):
            return False

    def get_custom_user_claims(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get custom claims for user."""
        try:
            user = auth.get_user(user_id)
            return user.custom_claims
        except (auth.FirebaseError, ValueError):
            return None


class UserProfileService:
    """Service for managing user profiles in Firestore."""

    def __init__(self) -> None:
        _ensure_firebase_initialized()

    def create_user_profile(
        self, user_id: str, email: str, data: dict[str, Any]
    ) -> bool:
        """Create user profile in Firestore using centralized firestore_service."""
        from services.firestore_service import save_user

        profile_data: dict[str, Any] = {
            "uid": user_id,
            "email": email,
            "role": data.get("role", "voter"),
            "full_name": data.get("full_name", ""),
            "language_preference": data.get("language_preference", "en"),
            "state": data.get("state", ""),
            "city": data.get("city", ""),
            "first_time_voter": data.get("first_time_voter", False),
            "profile_completed": False,
            "created_at": _server_timestamp(),
            "updated_at": _server_timestamp(),
            "last_login": _server_timestamp(),
        }

        result = save_user(user_id, profile_data)
        return result is not None

    def get_user_profile(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get user profile from Firestore using centralized firestore_service."""
        user_data = get_user(user_id)
        if user_data:
            return {"id": user_id, **user_data} if isinstance(user_data, dict) else None
        return None

    def upsert_user_profile(
        self,
        firebase_uid: str,
        email: str,
        name: Optional[str] = None,
        photo_url: Optional[str] = None,
        email_verified: bool = False,
        provider_id: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Create or update user profile using centralized firestore_service."""
        from services.firestore_service import create_or_update_user_profile

        return create_or_update_user_profile(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            photo_url=photo_url,
            role="user",
            auth_provider=provider_id or "firebase",
            email_verified=email_verified,
        )

    def update_user_profile(self, user_id: str, data: dict[str, Any]) -> bool:
        """Update user profile using centralized firestore_service."""
        from services.firestore_service import save_user

        data["updated_at"] = _server_timestamp()
        result = save_user(user_id, data)
        return result is not None

    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        from services.firestore_service import save_user

        result = save_user(user_id, {"last_login": _server_timestamp()})
        return result is not None

    def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile."""
        from services.firestore_service import get_firestore_client

        db = get_firestore_client()
        if not db:
            return False

        try:
            db.collection("users").document(user_id).delete()
            return True
        except (RuntimeError, ConnectionError) as e:
            logger.error("Failed to delete user profile: %s", e)
            return False

    def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user role."""
        profile = self.get_user_profile(user_id)
        if profile:
            return profile.get("role")
        return None

    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin."""
        return self.get_user_role(user_id) == "admin"

    def promote_to_admin(self, user_id: str) -> bool:
        """Promote user to admin."""
        return self.update_user_profile(
            user_id, {"role": "admin", "updated_at": _server_timestamp()}
        )


firebase_auth_service: FirebaseAuthService = FirebaseAuthService()
user_profile_service: UserProfileService = UserProfileService()
