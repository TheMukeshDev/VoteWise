"""
Base Service for VoteWise AI.

Generic CRUD operations to eliminate code duplication.
"""

from typing import Optional

from firebase_admin import firestore


class BaseService:
    """Base class for Firestore CRUD operations."""

    collection_name: str = ""
    soft_delete_field: str = "is_deleted"

    def __init__(self):
        self._db = None

    @property
    def db(self):
        """Get Firestore client."""
        if not self._db:
            try:
                self._db = firestore.client()
            except (RuntimeError, ConnectionError, ValueError):
                return None
        return self._db

    def _get_collection(self):
        """Get collection reference."""
        return self.db.collection(self.collection_name) if self.db else None

    def get_all(self, filters=None, order_by=None):
        """Get all documents from collection."""
        coll = self._get_collection()
        if not coll:
            return []

        try:
            query = coll.where(self.soft_delete_field, "!=", True)

            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.where(field, "==", value)

            if order_by:
                query = query.order_by(order_by, direction=firestore.Query.DESCENDING)

            docs = query.stream()
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            return result

        except (RuntimeError, ConnectionError, ValueError):
            return self._get_all_fallback(filters)

    def _get_all_fallback(self, filters=None):
        """Fallback: get all and filter in memory."""
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if data.get(self.soft_delete_field):
                    continue
                if filters:
                    skip = False
                    for field, value in filters.items():
                        if value is not None and data.get(field) != value:
                            skip = True
                            break
                    if skip:
                        continue
                data["id"] = doc.id
                results.append(data)
            return results
        except (RuntimeError, ConnectionError, ValueError):
            return []

    def get_by_id(self, doc_id: str):
        """Get a specific document by ID."""
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(doc_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get(self.soft_delete_field):
                    return None
                data["id"] = doc.id
                return data
            return None
        except (RuntimeError, ConnectionError, ValueError):
            return None

    def create(self, data, doc_id=None):
        """Create a new document."""
        coll = self._get_collection()
        if not coll:
            return None

        now = firestore.SERVER_TIMESTAMP
        data["created_at"] = now
        data["updated_at"] = now
        data[self.soft_delete_field] = False

        try:
            if doc_id:
                doc_ref = coll.document(doc_id)
            else:
                doc_ref = coll.document()

            doc_ref.set(data)
            data["id"] = doc_ref.id
            return data

        except (RuntimeError, ConnectionError, ValueError):
            return None

    def update(self, doc_id: str, data):
        """Update a document."""
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document(doc_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            data.pop("id", None)
            data["updated_at"] = firestore.SERVER_TIMESTAMP

            doc_ref.update(data)

            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            updated_data["id"] = doc_id
            return updated_data

        except (RuntimeError, ConnectionError, ValueError):
            return None

    def delete(self, doc_id: str, soft: bool = True):
        """Delete a document (soft delete by default)."""
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(doc_id)
            doc = doc_ref.get()

            if not doc.exists:
                return False

            if soft:
                doc_ref.update(
                    {
                        self.soft_delete_field: True,
                        "deleted_at": firestore.SERVER_TIMESTAMP,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                    }
                )
            else:
                doc_ref.delete()

            return True

        except (RuntimeError, ConnectionError, ValueError):
            return False

    def get_all_for_admin(self):
        """Get all documents including soft-deleted (for admin)."""
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            return result
        except (RuntimeError, ConnectionError, ValueError):
            return []
