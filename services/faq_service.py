"""
FAQ Service for VoteWise AI

Real Firestore CRUD operations for FAQs.
"""

import firebase_admin
from firebase_admin import firestore
from typing import Optional, List, Dict, Any


class FAQService:
    """Service for FAQ CRUD operations in Firestore."""

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
        """Get FAQs collection reference."""
        return self.db.collection("faqs") if self.db else None

    def get_all(
        self, category: Optional[str] = None, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all FAQs from Firestore.

        Args:
            category: Filter by category (optional)
            language: Filter by language (optional)

        Returns:
            List of FAQ documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            query = coll.where("is_deleted", "!=", True).where(
                "is_published", "==", True
            )

            if category:
                query = query.where("category", "==", category)
            if language:
                query = query.where("language", "==", language)

            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            # Fallback: get all and filter in memory
            try:
                docs = coll.stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    if (
                        data.get("is_deleted") != True
                        and data.get("is_published") == True
                    ):
                        if category and data.get("category") != category:
                            continue
                        if language and data.get("language") != language:
                            continue
                        results.append({"id": doc.id, **data})
                return results
            except Exception:
                return []

    def get_by_id(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific FAQ by ID.

        Args:
            faq_id: FAQ document ID

        Returns:
            FAQ data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(faq_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get("is_deleted") == True:
                    return None
                return {"id": doc.id, **data}
            return None
        except Exception:
            return None

    def create(
        self,
        question: str,
        answer: str,
        category: str = "general",
        language: str = "en",
        is_published: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new FAQ.

        Args:
            question: FAQ question
            answer: FAQ answer
            category: FAQ category
            language: Language code
            is_published: Publication status

        Returns:
            Created FAQ data
        """
        coll = self._get_collection()
        if not coll:
            raise Exception("Database not available")

        now = firestore.SERVER_TIMESTAMP

        faq_data = {
            "question": question,
            "answer": answer,
            "category": category,
            "language": language,
            "is_published": is_published,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = coll.document()
        doc_ref.set(faq_data)

        return {"id": doc_ref.id, **faq_data}

    def update(self, faq_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an FAQ.

        Args:
            faq_id: FAQ document ID
            data: Fields to update

        Returns:
            Updated FAQ data or None
        """
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document(faq_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            # Remove id from data if present
            data.pop("id", None)

            # Add updated_at timestamp
            data["updated_at"] = firestore.SERVER_TIMESTAMP

            # Only update provided fields
            doc_ref.update(data)

            updated_doc = doc_ref.get()
            return {"id": faq_id, **updated_doc.to_dict()}
        except Exception:
            return None

    def delete(self, faq_id: str, soft: bool = True) -> bool:
        """
        Delete an FAQ (soft delete by default).

        Args:
            faq_id: FAQ document ID
            soft: If True, soft delete; if False, hard delete

        Returns:
            True if successful
        """
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(faq_id)
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
        Get all FAQs including unpublished and soft-deleted (for admin).

        Returns:
            List of all FAQ documents
        """
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            return []


faq_service = FAQService()
