import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import os

# Initialize Firebase App
def init_firebase():
    if not firebase_admin._apps:
        cred_path = Config.FIREBASE_CREDENTIALS_PATH
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for environments without the file (e.g., local dev without key yet or GCP native)
            print("Warning: Firebase credentials file not found. Trying default credentials.")
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
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set(data, merge=True)
    return user_id

def get_user(user_id):
    db = get_db()
    if not db:
        return None
    doc = db.collection('users').document(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

# --- Election Operations ---

def get_election_process_data():
    db = get_db()
    if not db:
        return []
    docs = db.collection('elections').document('process').collection('steps').order_by('step_number').stream()
    return [doc.to_dict() for doc in docs]

def get_faqs_data():
    db = get_db()
    if not db:
        return []
    docs = db.collection('faqs').stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

def get_timeline_data():
    db = get_db()
    if not db:
        return []
    docs = db.collection('timelines').order_by('date').stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

# --- Reminders Operations ---

def save_reminder(user_id, reminder_data):
    db = get_db()
    if not db:
        return None
    # Add to subcollection
    doc_ref = db.collection('users').document(user_id).collection('reminders').document()
    doc_ref.set(reminder_data)
    return doc_ref.id
