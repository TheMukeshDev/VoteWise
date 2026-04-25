"""
Timeline Service for VoteWise AI

Real Firestore CRUD operations for Timelines.
"""

from firebase_admin import firestore
from typing import Optional, List, Dict, Any


class TimelineService:
    """Service for Timeline CRUD operations in Firestore."""

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
        """Get timelines collection reference."""
        return self.db.collection("timelines") if self.db else None

    def get_all(
        self, election_type: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all timelines from Firestore.

        Args:
            election_type: Filter by election type (optional)
            status: Filter by status (optional)

        Returns:
            List of timeline documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            # Filter out deleted records
            query = coll.where("is_deleted", "!=", True)

            if election_type:
                query = query.where("election_type", "==", election_type)
            if status:
                query = query.where("status", "==", status)

            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                results.append({"id": doc.id, **data})
            return sorted(
                results, key=lambda x: x.get("polling_date", ""), reverse=True
            )
        except Exception:
            # Fallback: get all and filter in memory
            try:
                docs = coll.stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    if data.get("is_deleted"):
                        continue
                    if election_type and data.get("election_type") != election_type:
                        continue
                    if status and data.get("status") != status:
                        continue
                    results.append({"id": doc.id, **data})
                return results
            except Exception:
                return []

    def get_by_id(self, timeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific timeline by ID.

        Args:
            timeline_id: Timeline document ID

        Returns:
            Timeline data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(timeline_id).get()
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
        election_type: str,
        region: str,
        polling_date: str,
        registration_deadline: Optional[str] = None,
        result_date: Optional[str] = None,
        status: str = "upcoming",
    ) -> Dict[str, Any]:
        """
        Create a new timeline.

        Args:
            election_type: Type of election
            region: Region for the timeline
            polling_date: Polling date
            registration_deadline: Registration deadline (optional)
            result_date: Result date (optional)
            status: Timeline status

        Returns:
            Created timeline data
        """
        coll = self._get_collection()
        if not coll:
            raise Exception("Database not available")

        now = firestore.SERVER_TIMESTAMP

        timeline_data = {
            "election_type": election_type,
            "region": region,
            "polling_date": polling_date,
            "registration_deadline": registration_deadline,
            "result_date": result_date,
            "status": status,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = coll.document()
        doc_ref.set(timeline_data)

        return {"id": doc_ref.id, **timeline_data}

    def update(
        self, timeline_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a timeline.

        Args:
            timeline_id: Timeline document ID
            data: Fields to update

        Returns:
            Updated timeline data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document(timeline_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            data.pop("id", None)
            data["updated_at"] = firestore.SERVER_TIMESTAMP

            doc_ref.update(data)

            updated_doc = doc_ref.get()
            return {"id": timeline_id, **updated_doc.to_dict()}
        except Exception:
            return None

    def delete(self, timeline_id: str, soft: bool = True) -> bool:
        """
        Delete a timeline (soft delete by default).

        Args:
            timeline_id: Timeline document ID
            soft: If True, soft delete; if False, hard delete

        Returns:
            True if successful
        """
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(timeline_id)
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
        Get all timelines including soft-deleted (for admin).

        Returns:
            List of all timeline documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []


timeline_service = TimelineService()
