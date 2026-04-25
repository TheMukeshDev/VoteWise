"""
Announcement Service for VoteWise AI

Real Firestore CRUD operations for Announcements.
"""

from firebase_admin import firestore
from typing import Optional, List, Dict, Any


class AnnouncementService:
    """Service for Announcement CRUD operations in Firestore."""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        """Get Firestore client."""
        if not self._db:
            try:
                self._db = firestore.client()
            except Exception:
                return None
        return self._db

    def _get_collection(self):
        """Get announcements collection reference."""
        return self.db.collection("announcements") if self.db else None

    def get_all(
        self, region: Optional[str] = None, priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all announcements from Firestore.

        Args:
            region: Filter by region (optional)
            priority: Filter by priority (optional)

        Returns:
            List of announcement documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            # Filter out deleted and inactive records
            query = coll.where("is_deleted", "!=", True).where("is_active", "==", True)

            if region:
                query = query.where("region", "==", region)
            if priority:
                query = query.where("priority", "==", priority)

            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                results.append({"id": doc.id, **data})
            return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)
        except Exception:
            # Fallback: get all and filter in memory
            try:
                docs = coll.stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    if data.get("is_deleted") or not data.get("is_active"):
                        continue
                    if region and data.get("region") != region:
                        continue
                    if priority and data.get("priority") != priority:
                        continue
                    results.append({"id": doc.id, **data})
                return results
            except Exception:
                return []

    def get_by_id(self, announcement_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific announcement by ID.

        Args:
            announcement_id: Announcement document ID

        Returns:
            Announcement data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(announcement_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get("is_deleted"):
                    return None
                return {"id": doc.id, **data}
            return None
        except Exception:
            return None

    def create(
        self,
        title: str,
        message: str,
        priority: str = "normal",
        region: str = "all",
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new announcement.

        Args:
            title: Announcement title
            message: Announcement message
            priority: Priority level (low, normal, high, urgent)
            region: Region for the announcement
            is_active: Active status

        Returns:
            Created announcement data
        """
        coll = self._get_collection()
        if not coll:
            raise Exception("Database not available")

        now = firestore.SERVER_TIMESTAMP

        announcement_data = {
            "title": title,
            "message": message,
            "priority": priority,
            "region": region,
            "is_active": is_active,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = coll.document()
        doc_ref.set(announcement_data)

        return {"id": doc_ref.id, **announcement_data}

    def update(
        self, announcement_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an announcement.

        Args:
            announcement_id: Announcement document ID
            data: Fields to update

        Returns:
            Updated announcement data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document(announcement_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            data.pop("id", None)
            data["updated_at"] = firestore.SERVER_TIMESTAMP

            doc_ref.update(data)

            updated_doc = doc_ref.get()
            return {"id": announcement_id, **updated_doc.to_dict()}
        except Exception:
            return None

    def delete(self, announcement_id: str, soft: bool = True) -> bool:
        """
        Delete an announcement (soft delete by default).

        Args:
            announcement_id: Announcement document ID
            soft: If True, soft delete; if False, hard delete

        Returns:
            True if successful
        """
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(announcement_id)
            doc = doc_ref.get()

            if not doc.exists:
                return False

            if soft:
                doc_ref.update(
                    {
                        "is_deleted": True,
                        "deleted_at": firestore.SERVER_TIMESTAMP,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                    }
                )
            else:
                doc_ref.delete()

            return True
        except Exception:
            return False

    def get_all_for_admin(self) -> List[Dict[str, Any]]:
        """
        Get all announcements including inactive and soft-deleted (for admin).

        Returns:
            List of all announcement documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []


announcement_service = AnnouncementService()
