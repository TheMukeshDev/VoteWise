import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from google.cloud import firestore as gcfirestore

logger = logging.getLogger(__name__)

_firestore_client: Optional[gcfirestore.Client] = None
_firebase_initialized = False


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
            logger.info(
                f"Firebase Admin SDK initialized successfully for project: {project_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
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
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(firebase_json, f)
                temp_path = f.name
            _firestore_client = gcfirestore.Client.from_service_account_json(temp_path)
            os.unlink(temp_path)
        else:
            _firestore_client = gcfirestore.Client()
        logger.info("Firestore client created successfully")
        return _firestore_client
    except Exception as e:
        logger.error(f"Failed to create Firestore client: {str(e)}")
        return None


def get_db() -> Optional[gcfirestore.Client]:
    """Alias for get_firestore_client() for backward compatibility."""
    return get_firestore_client()


def verify_firestore_connection() -> Dict[str, Any]:
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
    except Exception as e:
        logger.error(f"Firestore connection test failed: {str(e)}")
        return {"success": False, "connected": False, "message": str(e)}


# --- User Operations ---


def save_user(user_id: str, data: Dict[str, Any]) -> Optional[str]:
    """Save user data to Firestore."""
    db = get_firestore_client()
    if not db:
        logger.error(f"Failed to save user {user_id}: Firestore not available")
        return None

    try:
        data["updated_at"] = firestore.SERVER_TIMESTAMP
        doc_ref = db.collection("users").document(user_id)
        doc_ref.set(data, merge=True)
        logger.info(f"User {user_id} saved successfully")
        return user_id
    except Exception as e:
        logger.error(f"Failed to save user {user_id}: {str(e)}")
        return None


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user data from Firestore."""
    db = get_firestore_client()
    if not db:
        logger.warning(f"Failed to get user {user_id}: Firestore not available")
        return None

    try:
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {str(e)}")
        return None


def create_or_update_user_profile(
    firebase_uid: str,
    email: str,
    name: Optional[str] = None,
    photo_url: Optional[str] = None,
    role: str = "user",
    auth_provider: str = "firebase",
    email_verified: bool = False,
) -> Optional[Dict[str, Any]]:
    """Create or update user profile with all required fields."""
    db = get_firestore_client()
    if not db:
        logger.error(
            f"Failed to upsert profile for {firebase_uid}: Firestore not available"
        )
        return None

    try:
        existing = get_user(firebase_uid)
        now = datetime.utcnow()

        profile_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "name": name or email.split("@")[0] or "User",
            "photo_url": photo_url or "",
            "role": role,
            "auth_provider": auth_provider,
            "email_verified": email_verified,
            "last_login_at": now,
            "updated_at": now,
        }

        if existing:
            update_fields = {
                "last_login_at": now,
                "updated_at": now,
            }
            if name and name != existing.get("name"):
                update_fields["name"] = name
            if photo_url and photo_url != existing.get("photo_url"):
                update_fields["photo_url"] = photo_url

            db.collection("users").document(firebase_uid).update(update_fields)
            logger.info(f"User profile updated: uid={firebase_uid}, email={email}")
        else:
            profile_data["created_at"] = now
            db.collection("users").document(firebase_uid).set(profile_data)
            logger.info(f"User profile created: uid={firebase_uid}, email={email}")

        return get_user(firebase_uid)

    except Exception as e:
        logger.error(f"Failed to create/update profile for {firebase_uid}: {str(e)}")
        return None


# --- Election Operations ---


def get_election_process_data() -> List[Dict[str, Any]]:
    """Get election process steps from Firestore."""
    db = get_firestore_client()
    if not db:
        logger.warning("Firestore not available for election process data")
        return []
    try:
        docs = (
            db.collection("elections")
            .document("process")
            .collection("steps")
            .order_by("step_number")
            .stream()
        )
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        logger.error(f"Failed to get election process data: {str(e)}")
        return []


def get_faqs_data() -> List[Dict[str, Any]]:
    """Get FAQs from Firestore."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("faqs").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Failed to get FAQs: {str(e)}")
        return []


def get_timeline_data() -> List[Dict[str, Any]]:
    """Get timeline data from Firestore."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("timelines").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Failed to get timeline data: {str(e)}")
        return []


# --- Reminders Operations ---


def save_reminder(user_id: str, reminder_data: Dict[str, Any]) -> Optional[str]:
    """Save reminder for user."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        doc_ref = (
            db.collection("users").document(user_id).collection("reminders").document()
        )
        doc_ref.set(reminder_data)
        return doc_ref.id
    except Exception as e:
        logger.error(f"Failed to save reminder for {user_id}: {str(e)}")
        return None


def get_reminders(user_id: str) -> List[Dict[str, Any]]:
    """Get all reminders for user."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("users").document(user_id).collection("reminders").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Failed to get reminders for {user_id}: {str(e)}")
        return []


def get_reminder(user_id: str, reminder_id: str) -> Optional[Dict[str, Any]]:
    """Get specific reminder."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        doc = (
            db.collection("users")
            .document(user_id)
            .collection("reminders")
            .document(reminder_id)
            .get()
        )
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        return None
    except Exception as e:
        logger.error(f"Failed to get reminder {reminder_id}: {str(e)}")
        return None


def update_reminder(
    user_id: str, reminder_id: str, data: Dict[str, Any]
) -> Optional[str]:
    """Update reminder."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        doc_ref = (
            db.collection("users")
            .document(user_id)
            .collection("reminders")
            .document(reminder_id)
        )
        doc_ref.update(data)
        return reminder_id
    except Exception as e:
        logger.error(f"Failed to update reminder {reminder_id}: {str(e)}")
        return None


def delete_reminder(user_id: str, reminder_id: str) -> bool:
    """Delete reminder."""
    db = get_firestore_client()
    if not db:
        return False
    try:
        db.collection("users").document(user_id).collection("reminders").document(
            reminder_id
        ).delete()
        return True
    except Exception as e:
        logger.error(f"Failed to delete reminder {reminder_id}: {str(e)}")
        return False


# --- Bookmarks Operations ---


def save_bookmark(user_id: str, bookmark_data: Dict[str, Any]) -> Optional[str]:
    """Save bookmark for user."""
    db = get_firestore_client()
    if not db:
        return None
    try:
        bookmark_data["user_id"] = user_id
        doc_ref = (
            db.collection("users").document(user_id).collection("bookmarks").document()
        )
        doc_ref.set(bookmark_data)
        return doc_ref.id
    except Exception as e:
        logger.error(f"Failed to save bookmark for {user_id}: {str(e)}")
        return None


def get_bookmarks(user_id: str) -> List[Dict[str, Any]]:
    """Get all bookmarks for user."""
    db = get_firestore_client()
    if not db:
        return []
    try:
        docs = db.collection("users").document(user_id).collection("bookmarks").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Failed to get bookmarks for {user_id}: {str(e)}")
        return []


def get_bookmark_by_resource(
    user_id: str, resource_type: str, resource_id: str
) -> Optional[Dict[str, Any]]:
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
    except Exception as e:
        logger.error(f"Failed to get bookmark by resource: {str(e)}")
        return None


def delete_bookmark(user_id: str, bookmark_id: str) -> bool:
    """Delete bookmark."""
    db = get_firestore_client()
    if not db:
        return False
    try:
        db.collection("users").document(user_id).collection("bookmarks").document(
            bookmark_id
        ).delete()
        return True
    except Exception as e:
        logger.error(f"Failed to delete bookmark {bookmark_id}: {str(e)}")
        return False


init_firebase()
