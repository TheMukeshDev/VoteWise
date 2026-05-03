"""
Polling Guidance Service for VoteWise AI.

Real Firestore CRUD operations using BaseService.
"""

from typing import Any, List, Optional

from services.base_service import BaseService


class PollingGuidanceService(BaseService):
    """Service for Polling Guidance CRUD operations in Firestore."""

    collection_name = "polling_guidance"
    soft_delete_field = "is_deleted"

    def get_all(
        self,
        region: Optional[str] = None,
    ) -> List[dict]:
        """Get polling guidances with filters."""
        filters = {}
        if region:
            filters["region"] = region
        return super().get_all(filters=filters)

    def get_by_id(self, guidance_id: str) -> Optional[dict]:
        """Get polling guidance by ID."""
        return super().get_by_id(guidance_id)

    def create(
        self,
        region: str,
        title: str,
        description: str,
        help_links: Optional[list] = None,
        is_active: bool = True,
    ) -> Optional[dict]:
        """Create polling guidance."""
        data = {
            "region": region,
            "title": title,
            "description": description,
            "help_links": help_links or [],
            "is_active": is_active,
        }
        return super().create(data)

    def update(
        self,
        guidance_id: str,
        data: dict,
    ) -> Optional[dict]:
        """Update polling guidance."""
        return super().update(guidance_id, data)

    def delete(self, guidance_id: str, soft: bool = True) -> bool:
        """Delete polling guidance."""
        return super().delete(guidance_id, soft=soft)

    def get_all_for_admin(self) -> List[dict]:
        """Get all including soft-deleted."""
        return super().get_all_for_admin()


polling_guidance_service = PollingGuidanceService()
