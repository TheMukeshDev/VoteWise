"""Firestore Service for VoteWise AI"""

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as gcfirestore

from config import Config

logger = logging.getLogger(__name__)

_firestore_client: Optional[gcfirestore.Client] = None
_firebase_initialized: bool = False


def validate_document_id(doc_id: str) -> bool:
    """Validate document ID to prevent path traversal attacks.

    Only allows alphanumeric characters, underscores, and hyphens.
    """
    if not doc_id or not isinstance(doc_id, str):
        return False
    if ".." in doc_id or "/" in doc_id or "\\" in doc_id:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", doc_id))


def init_firebase() -> bool:
    """Initialize Firebase Admin SDK using FIREBASE_ADMIN_JSON from Secret Manager."""
    global _firebase_initialized

    if _firebase_initialized and firebase_admin._apps:
        return True

    if not firebase_admin._apps:
        try:
            firebase_json = Config.FIREBASE_ADMIN_JSON
            project_id = Config.FIREBASE_PROJECT_ID

            if not firebase_json:
                logger.error("FIREBASE_ADMIN_JSON environment variable not set")
                return False

            if not project_id:
                logger.error("FIREBASE_PROJECT_ID not configured")
                return False

            cred = credentials.Certificate(firebase_json)
            firebase_admin.initialize_app(cred, {"projectId": project_id})
            _firebase_initialized = True
            logger.info(f"Firebase Admin SDK initialized successfully for project: {project_id}")
            return True

        except (ValueError, RuntimeError, FileNotFoundError) as e:
            logger.error("Firebase initialization failed: %s", e)
            _firebase_initialized = False
            return False

    _firebase_initialized = True
    return True


def get_firestore_client() -> Optional[gcfirestore.Client]:
    """Get Firestore client singleton."""
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    if not init_firebase():
        logger.error("Cannot get Firestore client - Firebase not initialized")
        return None

    try:
        firebase_json = Config.FIREBASE_ADMIN_JSON
        if firebase_json:
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(firebase_json, f)
                temp_path = f.name
            _firestore_client = gcfirestore.Client.from_service_account_json(temp_path)
            os.unlink(temp_path)
        else:
            _firestore_client = gcfirestore.Client()
        logger.info("Firestore client created successfully")
        return _firestore_client
    except (ValueError, RuntimeError, FileNotFoundError):
        logger.error("Failed to create Firestore client")
        return None


def get_db() -> Optional[gcfirestore.Client]:
    """Alias for get_firestore_client() for backward compatibility."""
    return get_firestore_client()


def verify_firestore_connection() -> dict[str, Any]:
    """Verify Firestore connection with a test write/read operation."""
    db = get_firestore_client()
    if not db:
        return {
            "success": False,
            "connected": False,
            "message": "Failed to get Firestore client",
        }

    try:
        test_id = f"health_check_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        test_doc = db.collection("_health_check").document(test_id)
        test_doc.set(
            {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "created_at": firestore.SERVER_TIMESTAMP,
            }
        )

        doc = test_doc.get()
        if doc.exists:
            test_doc.delete()
            logger.info("Firestore connection verified successfully")
            return {
                "success": True,
                "connected": True,
                "message": "Firestore is working correctly",
            }
        return {
            "success": False,
            "connected": False,
            "message": "Could not read test document",
        }
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to verify Firestore connection: %s", e)
        return {
            "success": False,
            "connected": False,
            "message": f"Connection error: {e}",
        }


def get_user(user_id: str) -> Optional[dict[str, Any]]:
    """Get user data from Firestore."""
    db = get_firestore_client()
    if not db:
        logger.warning("Failed to get user %s: Firestore not available", user_id)
        return None

    try:
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get user %s: %s", user_id, e)
        return None


def create_or_update_user_profile(
    firebase_uid: str,
    email: str,
    name: Optional[str] = None,
    photo_url: Optional[str] = None,
    role: str = "user",
    auth_provider: str = "firebase",
    email_verified: bool = False,
) -> Optional[dict[str, Any]]:
    """Create or update user profile with all required fields."""
    db = get_firestore_client()
    if not db:
        logger.error("Failed to upsert profile for %s: Firestore not available", firebase_uid)
        return None

    try:
        existing = get_user(firebase_uid)
        now = datetime.now(timezone.utc)

        profile_data: dict[str, Any] = {
            "firebase_uid": firebase_uid,
            "email": email,
            "name": name or email.split("@")[0] if email else "User",
            "photo_url": photo_url or "",
            "role": role,
            "auth_provider": auth_provider,
            "email_verified": email_verified,
            "last_login_at": now,
            "updated_at": now,
        }

        if existing:
            update_fields: dict[str, Any] = {
                "last_login_at": now,
                "updated_at": now,
            }
            if name and name != existing.get("name"):
                update_fields["name"] = name
            if photo_url and photo_url != existing.get("photo_url"):
                update_fields["photo_url"] = photo_url

            db.collection("users").document(firebase_uid).update(update_fields)
            logger.info("User profile updated: uid=%s, email=%s", firebase_uid, email)
        else:
            profile_data["created_at"] = now
            db.collection("users").document(firebase_uid).set(profile_data)
            logger.info("User profile created: uid=%s, email=%s", firebase_uid, email)

        return get_user(firebase_uid)

    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to create/update profile for %s: %s", firebase_uid, e)
        return None


# --- Election Operations ---


def get_election_process_data() -> list[dict[str, Any]]:
    """Get election process steps from Firestore."""
    db = get_firestore_client()
    if not db:
        logger.warning("Firestore not available for election process data")
        return []
    try:
        docs = db.collection("elections").document("process").collection("steps").order_by("step_number").stream()
        return [doc.to_dict() for doc in docs]
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get election process data: %s", e)
        return []


def get_faqs_data() -> list[dict[str, Any]]:
    """Get FAQs from Firestore."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("faqs").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get FAQs: %s", e)
        return []


def get_timeline_data() -> list[dict[str, Any]]:
    """Get timeline data from Firestore."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("timelines").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get timeline data: %s", e)
        return []


# --- Reminders Operations ---


def save_reminder(user_id: str, reminder_data: dict[str, Any]) -> Optional[str]:
    """Save reminder for user."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        doc_ref = db.collection("users").document(user_id).collection("reminders").document()
        doc_ref.set(reminder_data)
        return doc_ref.id
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to save reminder for %s: %s", user_id, e)
        return None


def get_reminders(user_id: str) -> list[dict[str, Any]]:
    """Get all reminders for user."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("users").document(user_id).collection("reminders").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get reminders for %s: %s", user_id, e)
        return []


def get_reminder(user_id: str, reminder_id: str) -> Optional[dict[str, Any]]:
    """Get specific reminder."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        doc = db.collection("users").document(user_id).collection("reminders").document(reminder_id).get()
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        return None
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get reminder %s: %s", reminder_id, e)
        return None


def update_reminder(user_id: str, reminder_id: str, data: dict[str, Any]) -> Optional[str]:
    """Update reminder."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        doc_ref = db.collection("users").document(user_id).collection("reminders").document(reminder_id)
        doc_ref.update(data)
        return reminder_id
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to update reminder %s: %s", reminder_id, e)
        return None


def delete_reminder(user_id: str, reminder_id: str) -> bool:
    """Delete reminder."""
    db = get_firestore_client()
    if not db:
        return False
    try:
        db.collection("users").document(user_id).collection("reminders").document(reminder_id).delete()
        return True
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to delete reminder %s: %s", reminder_id, e)
        return False


# --- Bookmarks Operations ---


def save_bookmark(user_id: str, bookmark_data: dict[str, Any]) -> Optional[str]:
    """Save bookmark for user."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        bookmark_data["user_id"] = user_id
        doc_ref = db.collection("users").document(user_id).collection("bookmarks").document()
        doc_ref.set(bookmark_data)
        return doc_ref.id
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to save bookmark for %s: %s", user_id, e)
        return None


def get_bookmarks(user_id: str) -> list[dict[str, Any]]:
    """Get all bookmarks for user."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("users").document(user_id).collection("bookmarks").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get bookmarks for %s: %s", user_id, e)
        return []


def get_bookmark_by_resource(user_id: str, resource_type: str, resource_id: str) -> Optional[dict[str, Any]]:
    """Get bookmark by resource type and ID."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        docs = (
            db.collection("users")
            .document(user_id)
            .collection("bookmarks")
            .where("resource_type", "==", resource_type)
            .where("resource_id", "==", resource_id)
            .stream()
        )
        for doc in docs:
            return {"id": doc.id, **doc.to_dict()}
        return None
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to get bookmark by resource: %s", e)
        return None


def delete_bookmark(user_id: str, bookmark_id: str) -> bool:
    """Delete bookmark."""
    db = get_firestore_client()
    if not db:
        return False
    try:
        db.collection("users").document(user_id).collection("bookmarks").document(bookmark_id).delete()
        return True
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Failed to delete bookmark %s: %s", bookmark_id, e)
        return False


init_firebase()
