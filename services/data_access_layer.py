"""
Comprehensive Firestore Data Access Layer for VoteWise AI

Provides CRUD operations for all collections:
- users
- election_process
- timelines
- faqs
- reminders
- announcements
- bookmarks
- analytics
- polling_guidance
- settings
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional, Dict, Any
from datetime import datetime
from config import Config
import os


class FirestoreDB:
    """Comprehensive Firestore database access layer."""

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

    @property
    def db(self):
        """Get Firestore client."""
        if not self._initialized:
            self._init_firebase()
        try:
            return firestore.client()
        except Exception:
            return None

    # ==========================================
    # USERS COLLECTION
    # ==========================================

    def create_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Create a new user document."""
        db = self.db
        if not db:
            return False

        data["uid"] = user_id
        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("users").document(user_id).set(data)
            return True
        except Exception:
            return False

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
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

    def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user document."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("users").document(user_id).update(data)
            return True
        except Exception:
            return False

    def delete_user(self, user_id: str) -> bool:
        """Delete user document."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).delete()
            return True
        except Exception:
            return False

    def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users (admin only)."""
        db = self.db
        if not db:
            return []

        try:
            docs = db.collection("users").limit(limit).stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    # ==========================================
    # ELECTION_PROCESS COLLECTION
    # ==========================================

    def create_election_process(self, process_id: str, data: Dict[str, Any]) -> bool:
        """Create election process content."""
        db = self.db
        if not db:
            return False

        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("election_process").document(process_id).set(data)
            return True
        except Exception:
            return False

    def get_election_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get election process by ID."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("election_process").document(process_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None

    def get_all_election_processes(
        self, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all election processes."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("election_process").where("is_active", "==", True)
            if language:
                query = query.where("language", "==", language)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_election_process(self, process_id: str, data: Dict[str, Any]) -> bool:
        """Update election process."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("election_process").document(process_id).update(data)
            return True
        except Exception:
            return False

    def delete_election_process(self, process_id: str) -> bool:
        """Delete election process."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("election_process").document(process_id).delete()
            return True
        except Exception:
            return False

    # ==========================================
    # TIMELINES COLLECTION
    # ==========================================

    def create_timeline(self, timeline_id: str, data: Dict[str, Any]) -> bool:
        """Create timeline."""
        db = self.db
        if not db:
            return False

        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("timelines").document(timeline_id).set(data)
            return True
        except Exception:
            return False

    def get_timeline(self, timeline_id: str) -> Optional[Dict[str, Any]]:
        """Get timeline by ID."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("timelines").document(timeline_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None

    def get_timelines(
        self, election_type: Optional[str] = None, region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get timelines with filters."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("timelines")
            if election_type:
                query = query.where("election_type", "==", election_type)
            if region:
                query = query.where("region", "==", region)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_timeline(self, timeline_id: str, data: Dict[str, Any]) -> bool:
        """Update timeline."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("timelines").document(timeline_id).update(data)
            return True
        except Exception:
            return False

    def delete_timeline(self, timeline_id: str) -> bool:
        """Delete timeline."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("timelines").document(timeline_id).delete()
            return True
        except Exception:
            return False

    # ==========================================
    # FAQS COLLECTION
    # ==========================================

    def create_faq(self, faq_id: str, data: Dict[str, Any]) -> bool:
        """Create FAQ."""
        db = self.db
        if not db:
            return False

        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("faqs").document(faq_id).set(data)
            return True
        except Exception:
            return False

    def get_faq(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """Get FAQ by ID."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("faqs").document(faq_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None

    def get_faqs(
        self, category: Optional[str] = None, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get FAQs with filters."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("faqs").where("is_published", "==", True)
            if category:
                query = query.where("category", "==", category)
            if language:
                query = query.where("language", "==", language)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_faq(self, faq_id: str, data: Dict[str, Any]) -> bool:
        """Update FAQ."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("faqs").document(faq_id).update(data)
            return True
        except Exception:
            return False

    def delete_faq(self, faq_id: str) -> bool:
        """Delete FAQ."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("faqs").document(faq_id).delete()
            return True
        except Exception:
            return False

    # ==========================================
    # REMINDERS COLLECTION (User subcollection)
    # ==========================================

    def create_reminder(
        self, user_id: str, reminder_id: str, data: Dict[str, Any]
    ) -> bool:
        """Create reminder for user."""
        db = self.db
        if not db:
            return False

        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("users").document(user_id).collection("reminders").document(
                reminder_id
            ).set(data)
            return True
        except Exception:
            return False

    def get_reminder(self, user_id: str, reminder_id: str) -> Optional[Dict[str, Any]]:
        """Get reminder by ID."""
        db = self.db
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
        except Exception:
            return None

    def get_user_reminders(
        self, user_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all reminders for a user."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("users").document(user_id).collection("reminders")
            if status:
                query = query.where("status", "==", status)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_reminder(
        self, user_id: str, reminder_id: str, data: Dict[str, Any]
    ) -> bool:
        """Update reminder."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("users").document(user_id).collection("reminders").document(
                reminder_id
            ).update(data)
            return True
        except Exception:
            return False

    def delete_reminder(self, user_id: str, reminder_id: str) -> bool:
        """Delete reminder."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).collection("reminders").document(
                reminder_id
            ).delete()
            return True
        except Exception:
            return False

    # ==========================================
    # ANNOUNCEMENTS COLLECTION
    # ==========================================

    def create_announcement(self, announcement_id: str, data: Dict[str, Any]) -> bool:
        """Create announcement."""
        db = self.db
        if not db:
            return False

        data["published_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("announcements").document(announcement_id).set(data)
            return True
        except Exception:
            return False

    def get_announcement(self, announcement_id: str) -> Optional[Dict[str, Any]]:
        """Get announcement by ID."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("announcements").document(announcement_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None

    def get_announcements(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active announcements."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("announcements").where("is_active", "==", True)
            if region:
                query = query.where("region", "==", region)
            docs = query.order_by(
                "published_at", direction=firestore.Query.DESCENDING
            ).stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_announcement(self, announcement_id: str, data: Dict[str, Any]) -> bool:
        """Update announcement."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("announcements").document(announcement_id).update(data)
            return True
        except Exception:
            return False

    def delete_announcement(self, announcement_id: str) -> bool:
        """Delete announcement."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("announcements").document(announcement_id).delete()
            return True
        except Exception:
            return False

    # ==========================================
    # BOOKMARKS COLLECTION (User subcollection)
    # ==========================================

    def create_bookmark(
        self, user_id: str, bookmark_id: str, data: Dict[str, Any]
    ) -> bool:
        """Create bookmark for user."""
        db = self.db
        if not db:
            return False

        data["created_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("users").document(user_id).collection("bookmarks").document(
                bookmark_id
            ).set(data)
            return True
        except Exception:
            return False

    def get_user_bookmarks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookmarks for a user."""
        db = self.db
        if not db:
            return []

        try:
            docs = (
                db.collection("users")
                .document(user_id)
                .collection("bookmarks")
                .stream()
            )
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def delete_bookmark(self, user_id: str, bookmark_id: str) -> bool:
        """Delete bookmark."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("users").document(user_id).collection("bookmarks").document(
                bookmark_id
            ).delete()
            return True
        except Exception:
            return False

    # ==========================================
    # ANALYTICS COLLECTION
    # ==========================================

    def create_analytics(self, analytics_id: str, data: Dict[str, Any]) -> bool:
        """Create analytics record."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("analytics").document(analytics_id).set(data)
            return True
        except Exception:
            return False

    def get_analytics(
        self, metric_type: Optional[str] = None, start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get analytics data."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("analytics")
            if metric_type:
                query = query.where("metric_type", "==", metric_type)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def increment_analytics(self, metric_type: str, date: datetime) -> bool:
        """Increment analytics metric."""
        db = self.db
        if not db:
            return False

        doc_id = f"{metric_type}_{date.strftime('%Y%m%d')}"

        try:
            db.collection("analytics").document(doc_id).set(
                {
                    "metric_type": metric_type,
                    "date": firestore.SERVER_TIMESTAMP,
                    "metadata": {},
                },
                merge=True,
            )
            db.collection("analytics").document(doc_id).update(
                {"metric_value": firestore.Increment(1)}
            )
            return True
        except Exception:
            return False

    # ==========================================
    # POLLING_GUIDANCE COLLECTION
    # ==========================================

    def create_polling_guidance(self, guidance_id: str, data: Dict[str, Any]) -> bool:
        """Create polling guidance."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("polling_guidance").document(guidance_id).set(data)
            return True
        except Exception:
            return False

    def get_polling_guidance(self, guidance_id: str) -> Optional[Dict[str, Any]]:
        """Get polling guidance by ID."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("polling_guidance").document(guidance_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None

    def get_polling_guidances(
        self, region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get active polling guidances."""
        db = self.db
        if not db:
            return []

        try:
            query = db.collection("polling_guidance").where("is_active", "==", True)
            if region:
                query = query.where("region", "==", region)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_polling_guidance(self, guidance_id: str, data: Dict[str, Any]) -> bool:
        """Update polling guidance."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            db.collection("polling_guidance").document(guidance_id).update(data)
            return True
        except Exception:
            return False

    # ==========================================
    # SETTINGS COLLECTION
    # ==========================================

    def create_setting(self, key: str, value: Any) -> bool:
        """Create or update setting."""
        db = self.db
        if not db:
            return False

        try:
            db.collection("settings").document(key).set(
                {"key": key, "value": value, "updated_at": firestore.SERVER_TIMESTAMP}
            )
            return True
        except Exception:
            return False

    def get_setting(self, key: str) -> Optional[Any]:
        """Get setting value."""
        db = self.db
        if not db:
            return None

        try:
            doc = db.collection("settings").document(key).get()
            if doc.exists:
                return doc.to_dict().get("value")
            return None
        except Exception:
            return None

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        db = self.db
        if not db:
            return {}

        try:
            docs = db.collection("settings").stream()
            return {doc.id: doc.to_dict().get("value") for doc in docs}
        except Exception:
            return {}

    # ==========================================
    # VOTER_PREFERENCES SUB_COLLECTION
    # ==========================================

    def create_or_update_preferences(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Create or update voter preferences."""
        db = self.db
        if not db:
            return False

        data["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            doc_ref = (
                db.collection("users")
                .document(user_id)
                .collection("preferences")
                .document("main")
            )
            doc_ref.set(data, merge=True)
            return True
        except Exception:
            return False

    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get voter preferences."""
        db = self.db
        if not db:
            return None

        try:
            doc = (
                db.collection("users")
                .document(user_id)
                .collection("preferences")
                .document("main")
                .get()
            )
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            return None


# Singleton instance
firestore_db = FirestoreDB()
