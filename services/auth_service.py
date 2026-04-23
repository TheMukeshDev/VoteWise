"""
Firebase Authentication Service for VoteWise AI

Handles:
- Email/password authentication
- Google Sign-In
- User session management
- Role-based access control
"""

import firebase_admin
from firebase_admin import auth, credentials, firestore
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config
import os


class FirebaseAuthService:
    """Service for handling Firebase Authentication operations."""

    def __init__(self):
        self._initialized = False
        self._init_firebase()

    def _init_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not firebase_admin._apps:
            cred_path = Config.FIREBASE_CREDENTIALS_PATH
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
            else:
                try:
                    firebase_admin.initialize_app()
                    self._initialized = True
                except Exception as e:
                    print(f"Firebase initialization warning: {e}")

    @property
    def db(self):
        """Get Firestore client."""
        if not self._initialized:
            self._init_firebase()
        try:
            return firestore.client()
        except Exception:
            return None

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and return claims.

        Args:
            id_token: Firebase ID token from client

        Returns:
            Decoded token claims or None if invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.InvalidIdTokenError:
            return None
        except auth.ExpiredIdTokenError:
            return None
        except Exception:
            return None

    def create_custom_token(
        self, user_id: str, additional_claims: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create custom JWT token for user.

        Args:
            user_id: Firebase user ID
            additional_claims: Additional claims to include

        Returns:
            Custom token string or None on error
        """
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
        """
        Get user from Firebase Auth.

        Args:
            user_id: Firebase user ID

        Returns:
            User record or None
        """
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
        """
        Create new user with email/password.

        Args:
            email: User email
            password: User password
            display_name: Display name (optional)

        Returns:
            Created user record or None on error
        """
        try:
            user = auth.create_user(
                email=email, password=password, display_name=display_name
            )
            return {"uid": user.uid, "email": user.email}
        except auth.EmailAlreadyExistsError:
            raise ValueError("User with this email already exists")
        except auth.InvalidPasswordError:
            raise ValueError("Invalid password")
        except Exception as e:
            raise ValueError(str(e))

    def update_user(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update user information.

        Args:
            user_id: Firebase user ID
            **kwargs: Fields to update (display_name, email, etc.)

        Returns:
            Updated user record or None
        """
        try:
            user = auth.update_user(user_id, **kwargs)
            return {"uid": user.uid, "email": user.email}
        except Exception:
            return None

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user from Firebase Auth.

        Args:
            user_id: Firebase user ID

        Returns:
            True if successful
        """
        try:
            auth.delete_user(user_id)
            return True
        except Exception:
            return False

    def set_custom_user_claims(self, user_id: str, claims: Dict[str, Any]) -> bool:
        """
        Set custom claims for user (e.g., role).

        Args:
            user_id: Firebase user ID
            claims: Claims to set (e.g., {"role": "admin"})

        Returns:
            True if successful
        """
        try:
            auth.set_custom_user_claims(user_id, claims)
            return True
        except Exception:
            return None

    def get_custom_user_claims(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get custom claims for user.

        Args:
            user_id: Firebase user ID

        Returns:
            Custom claims or None
        """
        try:
            user = auth.get_user(user_id)
            return user.custom_claims
        except Exception:
            return None


class UserProfileService:
    """Service for managing user profiles in Firestore."""

    def __init__(self):
        self._initialized = False
        self._init_firebase()

    def _init_firebase(self):
        """Initialize Firebase."""
        if not firebase_admin._apps:
            cred_path = Config.FIREBASE_CREDENTIALS_PATH
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True

    @property
    def db(self):
        """Get Firestore client."""
        if not self._initialized:
            self._init_firebase()
        try:
            return firestore.client()
        except Exception:
            return None

    def create_user_profile(
        self, user_id: str, email: str, data: Dict[str, Any]
    ) -> bool:
        """
        Create user profile in Firestore.

        Args:
            user_id: Firebase user ID
            email: User email
            data: Additional user data

        Returns:
            True if successful
        """
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
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "last_login": firestore.SERVER_TIMESTAMP,
        }

        try:
            db.collection("users").document(user_id).set(profile_data)
            return True
        except Exception:
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firestore.

        Args:
            user_id: Firebase user ID

        Returns:
            User profile or None
        """
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
        """
        Update user profile.

        Args:
            user_id: Firebase user ID
            data: Fields to update

        Returns:
            True if successful
        """
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("users").document(user_id).update(data)
            return True
        except Exception:
            return False

    def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: Firebase user ID

        Returns:
            True if successful
        """
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).update(
                {"last_login": firestore.SERVER_TIMESTAMP}
            )
            return True
        except Exception:
            return False

    def delete_user_profile(self, user_id: str) -> bool:
        """
        Delete user profile.

        Args:
            user_id: Firebase user ID

        Returns:
            True if successful
        """
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).delete()
            return True
        except Exception:
            return False

    def get_user_role(self, user_id: str) -> Optional[str]:
        """
        Get user role.

        Args:
            user_id: Firebase user ID

        Returns:
            Role string or None
        """
        profile = self.get_user_profile(user_id)
        if profile:
            return profile.get("role")
        return None

    def is_admin(self, user_id: str) -> bool:
        """
        Check if user is admin.

        Args:
            user_id: Firebase user ID

        Returns:
            True if admin
        """
        return self.get_user_role(user_id) == "admin"

    def promote_to_admin(self, user_id: str) -> bool:
        """
        Promote user to admin.

        Args:
            user_id: Firebase user ID

        Returns:
            True if successful
        """
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).update(
                {"role": "admin", "updated_at": firestore.SERVER_TIMESTAMP}
            )
            return True
        except Exception:
            return False


firebase_auth_service = FirebaseAuthService()
user_profile_service = UserProfileService()
