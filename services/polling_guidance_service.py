"""
Polling Guidance Service for VoteWise AI

Real Firestore CRUD operations for Polling Guidance.
"""

from firebase_admin import firestore
from typing import Optional, List, Dict, Any


class PollingGuidanceService:
    """Service for Polling Guidance CRUD operations in Firestore."""

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
        """Get polling_guidance collection reference."""
        return self.db.collection("polling_guidance") if self.db else None

    def get_all(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all polling guidance from Firestore.

        Args:
            region: Filter by region (optional)

        Returns:
            List of polling guidance documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            query = coll.where("is_deleted", "!=", True).where("is_active", "==", True)

            if region:
                query = query.where("region", "==", region)

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
                    if region and data.get("region") != region:
                        continue
                    results.append({"id": doc.id, **data})
                return results
            except Exception:
                return []

    def get_by_id(self, guidance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific polling guidance by ID.

        Args:
            guidance_id: Polling guidance document ID

        Returns:
            Polling guidance data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(guidance_id).get()
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
        region: str,
        title: str,
        description: str,
        help_links: Optional[List[Dict]] = None,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new polling guidance.

        Args:
            region: Region for the guidance
            title: Guidance title
            description: Guidance description
            help_links: List of help links
            is_active: Active status

        Returns:
            Created polling guidance data
        """
        coll = self._get_collection()
        if not coll:
            raise Exception("Database not available")

        now = firestore.SERVER_TIMESTAMP

        guidance_data = {
            "region": region,
            "title": title,
            "description": description,
            "help_links": help_links or [],
            "is_active": is_active,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = coll.document()
        doc_ref.set(guidance_data)

        return {"id": doc_ref.id, **guidance_data}

    def update(
        self, guidance_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a polling guidance.

        Args:
            guidance_id: Polling guidance document ID
            data: Fields to update

        Returns:
            Updated polling guidance data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document(guidance_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            data.pop("id", None)
            data["updated_at"] = firestore.SERVER_TIMESTAMP

            doc_ref.update(data)

            updated_doc = doc_ref.get()
            return {"id": guidance_id, **updated_doc.to_dict()}
        except Exception:
            return None

    def delete(self, guidance_id: str, soft: bool = True) -> bool:
        """
        Delete a polling guidance (soft delete by default).

        Args:
            guidance_id: Polling guidance document ID
            soft: If True, soft delete; if False, hard delete

        Returns:
            True if successful
        """
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(guidance_id)
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
        Get all polling guidance including inactive and soft-deleted (for admin).

        Returns:
            List of all polling guidance documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []


polling_guidance_service = PollingGuidanceService()
