"""
FAQ Service for VoteWise AI

Real Firestore CRUD operations for FAQs with caching.
"""

from firebase_admin import firestore
from typing import Optional, List, Dict, Any

from services.cache_service import (
    get_cached,
    set_cached,
    delete_cached,
    CACHE_KEYS,
    TTL_VALUES,
)


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
        """Get all FAQs from Firestore with caching."""
        cache_key = f"{CACHE_KEYS['faqs']}:{category}:{language}"
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        faqs, _ = self.get_all_paginated(category, language, page=1, limit=1000)
        if faqs:
            set_cached(cache_key, faqs, TTL_VALUES["faqs"])
        return faqs

    def get_all_paginated(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple:
        """Get FAQs with pagination."""
        all_faqs = self._get_all_no_cache(category, language)
        total = len(all_faqs) if all_faqs else 0
        start = (page - 1) * limit
        end = start + limit
        return (all_faqs[start:end] if all_faqs else [], total)

    def _get_all_no_cache(
        self, category: Optional[str] = None, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all FAQs without caching."""
        coll = self._get_collection()
        if not coll:
            return []

        try:
            docs = coll.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if data and data.get("is_published"):
                    if category and data.get("category") != category:
                        continue
                    if language and data.get("language") != language:
                        continue
                    results.append({"id": doc.id, **data})
            return results
        except Exception:
            return []

    def get_by_id(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific FAQ by ID."""
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc = coll.document(faq_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
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
    ) -> Optional[Dict[str, Any]]:
        """Create a new FAQ and invalidate cache."""
        coll = self._get_collection()
        if not coll:
            return None

        try:
            doc_ref = coll.document()
            doc_ref.set(
                {
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "language": language,
                    "is_published": is_published,
                    "is_deleted": False,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                }
            )

            # Invalidate FAQ cache on create
            for lang in ["en", "hi", "kn", "ta"]:
                for cat in [None, "general", "registration", "voting"]:
                    delete_cached(f"{CACHE_KEYS['faqs']}:{cat}:{lang}")

            return {"id": doc_ref.id}
        except Exception:
            return None

    def update(self, faq_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an FAQ."""
        coll = self._get_collection()
        if not coll:
            return None

        try:
            data["updated_at"] = firestore.SERVER_TIMESTAMP
            coll.document(faq_id).update(data)

            # Invalidate cache
            for lang in ["en", "hi", "kn", "ta"]:
                for cat in [None, "general", "registration", "voting"]:
                    delete_cached(f"{CACHE_KEYS['faqs']}:{cat}:{lang}")

            return self.get_by_id(faq_id)
        except Exception:
            return None

    def delete(self, faq_id: str, soft: bool = True) -> bool:
        """Delete an FAQ (soft delete by default)."""
        coll = self._get_collection()
        if not coll:
            return False

        try:
            doc_ref = coll.document(faq_id)
            if soft:
                doc_ref.update({"is_deleted": True, "is_published": False})
            else:
                doc_ref.delete()

            # Invalidate cache
            for lang in ["en", "hi", "kn", "ta"]:
                for cat in [None, "general", "registration", "voting"]:
                    delete_cached(f"{CACHE_KEYS['faqs']}:{cat}:{lang}")

            return True
        except Exception:
            return False


faq_service = FAQService()
