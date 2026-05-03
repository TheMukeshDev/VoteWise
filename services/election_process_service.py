"""
Election Process Service for VoteWise AI.

Real Firestore CRUD operations using BaseService.
"""

from typing import Any, List, Optional

from services.base_service import BaseService


class ElectionProcessService(BaseService):
    """Service for Election Process CRUD operations in Firestore."""

    collection_name = "election_process"
    soft_delete_field = "is_deleted"

    def get_all(
        self,
        language: Optional[str] = None,
    ) -> List[dict]:
        """Get election processes with filters."""
        filters = {}
        if language:
            filters["language"] = language
        return super().get_all(filters=filters)

    def get_by_id(self, process_id: str) -> Optional[dict]:
        """Get election process by ID."""
        return super().get_by_id(process_id)

    def create(
        self,
        title: str,
        intro: str,
        steps: list,
        tips: Optional[list] = None,
        language: str = "en",
        is_active: bool = True,
    ) -> Optional[dict]:
        """Create election process."""
        data = {
            "title": title,
            "intro": intro,
            "steps": steps,
            "tips": tips or [],
            "language": language,
            "is_active": is_active,
        }
        return super().create(data)

    def update(self, process_id: str, data: dict) -> Optional[dict]:
        """Update election process."""
        return super().update(process_id, data)

    def delete(self, process_id: str, soft: bool = True) -> bool:
        """Delete election process."""
        return super().delete(process_id, soft=soft)

    def get_all_for_admin(self) -> List[dict]:
        """Get all including soft-deleted."""
        return super().get_all_for_admin()


election_process_service = ElectionProcessService()
