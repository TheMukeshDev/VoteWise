"""
Election Process Service for VoteWise AI

Real Firestore CRUD operations for Election Process (guides).
"""

from firebase_admin import firestore
from typing import Optional, List, Dict, Any


class ElectionProcessService:
    """Service for Election Process CRUD operations in Firestore."""

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
        """Get election_process collection reference."""
        return self.db.collection("election_process") if self.db else None

    def get_all(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all election process guides from Firestore.

        Args:
            language: Filter by language (optional)

        Returns:
            List of election process documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            query = coll.where("is_deleted", "!=", True).where("is_active", "==", True)

            if language:
                query = query.where("language", "==", language)

            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                results.append({"id": doc.id, **data})
            return results
        except Exception:
            try:
                docs = coll.stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    if data.get("is_deleted") or not data.get("is_active"):
                        continue
                    if language and data.get("language") != language:
                        continue
                    results.append({"id": doc.id, **data})
                return results
            except Exception:
                return []

    def get_by_id(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific election process by ID.

        Args:
            process_id: Election process document ID

        Returns:
            Election process data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(process_id).get()
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
        intro: str,
        steps: List[Dict],
        tips: Optional[List[str]] = None,
        language: str = "en",
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new election process guide.

        Args:
            title: Guide title
            intro: Introduction
            steps: List of step dictionaries
            tips: List of tips
            language: Language code
            is_active: Active status

        Returns:
            Created election process data
        """
        coll = self._get_collection()
        if not coll:
            raise Exception("Database not available")

        now = firestore.SERVER_TIMESTAMP

        process_data = {
            "title": title,
            "intro": intro,
            "steps": steps,
            "tips": tips or [],
            "language": language,
            "is_active": is_active,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = coll.document()
        doc_ref.set(process_data)

        return {"id": doc_ref.id, **process_data}

    def update(self, process_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an election process.

        Args:
            process_id: Election process document ID
            data: Fields to update

        Returns:
            Updated election process data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document(process_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            data.pop("id", None)
            data["updated_at"] = firestore.SERVER_TIMESTAMP

            doc_ref.update(data)

            updated_doc = doc_ref.get()
            return {"id": process_id, **updated_doc.to_dict()}
        except Exception:
            return None

    def delete(self, process_id: str, soft: bool = True) -> bool:
        """
        Delete an election process (soft delete by default).

        Args:
            process_id: Election process document ID
            soft: If True, soft delete; if False, hard delete

        Returns:
            True if successful
        """
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(process_id)
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
        Get all election processes including inactive and soft-deleted (for admin).

        Returns:
            List of all election process documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []


election_process_service = ElectionProcessService()
