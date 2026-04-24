"""
Firebase Authentication Service for VoteWise AI

Handles:
- Email/password authentication
- Google Sign-In
- User session management
- Role-based access control
"""

import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
import datetime
from typing import Optional, Dict, Any
from config import Config
import os


def _get_firestore_client():
    """Get Firestore client with error handling."""
    try:
        return firestore.Client()
    except Exception:
        return None


def _server_timestamp():
    """Get server timestamp for Firestore."""
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


_firebase_initialized = False


def _ensure_firebase_initialized():
    """Ensure Firebase is initialized exactly once."""
    global _firebase_initialized
    if _firebase_initialized:
        return True

    if not firebase_admin._apps:
        private_key = Config.FIREBASE_PRIVATE_KEY
        if private_key:
            private_key = private_key.replace("\\n", "\n")

        creds_dict = {
            "type": "service_account",
            "project_id": Config.FIREBASE_PROJECT_ID,
            "private_key_id": Config.FIREBASE_PRIVATE_KEY_ID,
            "private_key": private_key,
            "client_email": Config.FIREBASE_CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        if creds_dict.get("private_key"):
            try:
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(
                    cred, {"projectId": Config.FIREBASE_PROJECT_ID}
                )
            except Exception as e:
                print(f"Firebase initialization warning: {e}")
                try:
                    firebase_admin.initialize_app()
                except Exception:
                    pass
        else:
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Firebase initialization warning: {e}")

    _firebase_initialized = True
    return _firebase_initialized


class FirebaseAuthService:
    """Service for handling Firebase Authentication operations."""

    def __init__(self):
        _ensure_firebase_initialized()

    @property
    def db(self):
        """Get Firestore client."""
        return _get_firestore_client()

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return claims."""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception:
            return None

    def create_custom_token(
        self, user_id: str, additional_claims: Optional[Dict] = None
    ) -> Optional[str]:
        """Create custom JWT token for user."""
        try:
            custom_token = auth.create_custom_token(user_id, additional_claims or {})
            return (
                custom_token.decode("utf-8")
                if isinstance(custom_token, bytes)
                else custom_token
            )
        except Exception:
            return None

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
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
        except Exception:
            return None

    def create_user(
        self, email: str, password: str, display_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create new user with email/password."""
        try:
            user = auth.create_user(
                email=email, password=password, display_name=display_name
            )
            return {"uid": user.uid, "email": user.email}
        except Exception as e:
            raise ValueError(str(e))

    def update_user(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user information."""
        try:
            user = auth.update_user(user_id, **kwargs)
            return {"uid": user.uid, "email": user.email}
        except Exception:
            return None

    def delete_user(self, user_id: str) -> bool:
        """Delete user from Firebase Auth."""
        try:
            auth.delete_user(user_id)
            return True
        except Exception:
            return False

    def set_custom_user_claims(
        self, user_id: str, claims: Dict[str, Any]
    ) -> Optional[bool]:
        """Set custom claims for user (e.g., role)."""
        try:
            auth.set_custom_user_claims(user_id, claims)
            return True
        except Exception:
            return False

    def get_custom_user_claims(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get custom claims for user."""
        try:
            user = auth.get_user(user_id)
            return user.custom_claims
        except Exception:
            return None


class UserProfileService:
    """Service for managing user profiles in Firestore."""

    def __init__(self):
        _ensure_firebase_initialized()

    @property
    def db(self):
        """Get Firestore client."""
        return _get_firestore_client()

    def create_user_profile(
        self, user_id: str, email: str, data: Dict[str, Any]
    ) -> bool:
        """Create user profile in Firestore."""
        db = self.db
        if not db:
            return False

        profile_data = {
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

        try:
            db.collection("users").document(user_id).set(profile_data)
            return True
        except Exception:
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from Firestore."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("users").document(user_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None

    def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user profile."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = _server_timestamp()

        try:
            db.collection("users").document(user_id).update(data)
            return True
        except Exception:
            return False

    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).update(
                {"last_login": _server_timestamp()}
            )
            return True
        except Exception:
            return False

    def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).delete()
            return True
        except Exception:
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
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).update(
                {"role": "admin", "updated_at": _server_timestamp()}
            )
            return True
        except Exception:
            return False


firebase_auth_service = FirebaseAuthService()
user_profile_service = UserProfileService()
