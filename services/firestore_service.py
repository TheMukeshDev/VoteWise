import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import os


def _get_firebase_credentials():
    """Get Firebase credentials from env variables."""
    private_key = Config.FIREBASE_PRIVATE_KEY
    if private_key:
        private_key = private_key.replace("\\n", "\n")

    return {
        "type": "service_account",
        "project_id": Config.FIREBASE_PROJECT_ID,
        "private_key_id": Config.FIREBASE_PRIVATE_KEY_ID,
        "private_key": private_key,
        "client_email": Config.FIREBASE_CLIENT_EMAIL,
        "token_uri": "https://oauth2.googleapis.com/token",
    }


def init_firebase():
    """Initialize Firebase App using env credentials."""
    if not firebase_admin._apps:
        try:
            creds_dict = _get_firebase_credentials()
            if creds_dict.get("private_key"):
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(
                    cred, {"projectId": Config.FIREBASE_PROJECT_ID}
                )
            else:
                raise ValueError("FIREBASE_PRIVATE_KEY not found in environment")
        except Exception as e:
            print(f"Warning: Firebase initialization failed: {e}")
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Failed to initialize Firebase: {e}")


# Attempt initialization on import
init_firebase()


def get_db():
    try:
        return firestore.client()
    except Exception as e:
        print(f"Firestore not available: {e}")
        return None


# --- User Operations ---


def save_user(user_id, data):
    db = get_db()
    if not db:
        return None
    doc_ref = db.collection("users").document(user_id)
    doc_ref.set(data, merge=True)
    return user_id


def get_user(user_id):
    db = get_db()
    if not db:
        return None
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


# --- Election Operations ---


def get_election_process_data():
    db = get_db()
    if not db:
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
    except Exception:
        return []


def get_faqs_data():
    db = get_db()
    if not db:
        return []
    docs = db.collection("faqs").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def get_timeline_data():
    db = get_db()
    if not db:
        return []
    docs = db.collection("timelines").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


# --- Reminders Operations ---


def save_reminder(user_id, reminder_data):
    db = get_db()
    if not db:
        return None
    doc_ref = (
        db.collection("users").document(user_id).collection("reminders").document()
    )
    doc_ref.set(reminder_data)
    return doc_ref.id


def get_reminders(user_id):
    db = get_db()
    if not db:
        return []
    docs = db.collection("users").document(user_id).collection("reminders").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def get_reminder(user_id, reminder_id):
    db = get_db()
    if not db:
        return None
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


def update_reminder(user_id, reminder_id, data):
    db = get_db()
    if not db:
        return None
    doc_ref = (
        db.collection("users")
        .document(user_id)
        .collection("reminders")
        .document(reminder_id)
    )
    doc_ref.update(data)
    return reminder_id


def delete_reminder(user_id, reminder_id):
    db = get_db()
    if not db:
        return False
    db.collection("users").document(user_id).collection("reminders").document(
        reminder_id
    ).delete()
    return True


# --- Bookmarks Operations ---


def save_bookmark(user_id, bookmark_data):
    db = get_db()
    if not db:
        return None
    bookmark_data["user_id"] = user_id
    doc_ref = (
        db.collection("users").document(user_id).collection("bookmarks").document()
    )
    doc_ref.set(bookmark_data)
    return doc_ref.id


def get_bookmarks(user_id):
    db = get_db()
    if not db:
        return []
    docs = db.collection("users").document(user_id).collection("bookmarks").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def get_bookmark_by_resource(user_id, resource_type, resource_id):
    db = get_db()
    if not db:
        return None
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


def delete_bookmark(user_id, bookmark_id):
    db = get_db()
    if not db:
        return False
    db.collection("users").document(user_id).collection("bookmarks").document(
        bookmark_id
    ).delete()
    return True
