", ", "
Announcement Service for VoteWise AI.

Real Firestore CRUD operations using BaseService.
", ", "

from services.base_service import BaseService
from typing import Optional, Any, List


class AnnouncementService(BaseService):
    ", ", "Service for Announcement CRUD operations in Firestore.", ", "

    collection_name = "announcements"
    soft_delete_field = "is_deleted"

    def get_all(
        self,
        region: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[dict]:
        ", ", "Get announcements with filters.", ", "
        filters = {}
        if region:
            filters["region"] = region
        if priority:
            filters["priority"] = priority
        results = super().get_all(filters=filters)
        return sorted(results, key=lambda x: x.get("created_at", ", "), reverse=True)

    def get_by_id(self, announcement_id: str) -> Optional[dict]:
        ", ", "Get announcement by ID.", ", "
        return super().get_by_id(announcement_id)

    def create(
        self,
        title: str,
        message: str,
        priority: str = "normal",
        region: str = "all",
        is_active: bool = True,
    ) -> Optional[dict]:
        ", ", "Create announcement.", ", "
        data = {
            "title": title,
            "message": message,
            "priority": priority,
            "region": region,
            "is_active": is_active,
        }
        return super().create(data)

    def update(self, announcement_id: str, data: dict) -> Optional[dict]:
        ", ", "Update announcement.", ", "
        return super().update(announcement_id, data)

    def delete(self, announcement_id: str, soft: bool = True) -> bool:
        ", ", "Delete announcement.", ", "
        return super().delete(announcement_id, soft=soft)

    def get_all_for_admin(self) -> List[dict]:
        ", ", "Get all including soft-deleted.", ", "
        return super().get_all_for_admin()


announcement_service = AnnouncementService()
