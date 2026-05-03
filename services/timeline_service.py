"""
Timeline Service for VoteWise AI.

Real Firestore CRUD operations for Timelines using BaseService.
"""

from typing import Any, Dict, List, Optional

from services.base_service import BaseService


class TimelineService(BaseService):
    """Service for Timeline CRUD operations in Firestore."""

    collection_name = "timelines"
    soft_delete_field = "is_deleted"

    def get_all(
        self,
        election_type: Optional[str] = None,
        status: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all timelines with filters."""
        filters = {}
        if election_type:
            filters["election_type"] = election_type
        if status:
            filters["status"] = status
        if region:
            filters["region"] = region

        results = super().get_all(filters=filters, order_by="polling_date")
        return sorted(results, key=lambda x: x.get("polling_date" ""), reverse=True)

    def get_by_id(self, timeline_id: str) -> Optional[Dict[str, Any]]:
        """Get timeline by ID."""
        return super().get_by_id(timeline_id)

    def create(
        self,
        election_type: str,
        region: str,
        polling_date: str,
        registration_deadline: Optional[str] = None,
        result_date: Optional[str] = None,
        status: str = "upcoming",
    ) -> Optional[Dict[str, Any]]:
        """Create timeline."""
        data = {
            "election_type": election_type,
            "region": region,
            "polling_date": polling_date,
            "registration_deadline": registration_deadline,
            "result_date": result_date,
            "status": status,
        }
        return super().create(data)

    def update(self, timeline_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update timeline."""
        return super().update(timeline_id, data)

    def delete(self, timeline_id: str, soft: bool = True) -> bool:
        """Delete timeline."""
        return super().delete(timeline_id, soft=soft)

    def get_all_for_admin(self) -> List[Dict[str, Any]]:
        """Get all including soft-deleted."""
        return super().get_all_for_admin()


timeline_service = TimelineService()
