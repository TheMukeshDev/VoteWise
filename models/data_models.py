"""
Firestore Data Models for VoteWise AI

Defines schemas for all collections:
1. users
2. election_process
3. timelines
4. faqs
5. reminders
6. announcements
7. bookmarks
8. analytics
9. polling_guidance
10. settings
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class UserRole(str, Enum):
    VOTER = "voter"
    ADMIN = "admin"


class ReminderType(str, Enum):
    REGISTRATION_DEADLINE = "registration_deadline"
    POLLING_DAY = "polling_day"
    RESULT_DAY = "result_day"
    CUSTOM = "custom"


class ReminderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AnnouncementPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ResourceType(str, Enum):
    FAQ = "faq"
    GUIDE = "guide"
    TIMELINE = "timeline"
    POLLING = "polling"


@dataclass
class UserProfile:
    """User profile model."""

    uid: str
    email: str
    role: str = "voter"
    full_name: str = ""
    language_preference: str = "en"
    state: str = ""
    city: str = ""
    first_time_voter: bool = False
    profile_completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Firestore."""
        data = asdict(self)
        data = {k: v for k, v in data.items() if v is not None}
        return data


@dataclass
class ElectionProcess:
    """Election process content model."""

    title: str
    category: str
    language: str = "en"
    intro: str = ""
    steps: list[dict[str, str]] = field(default_factory=list)
    tips: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ElectionTimeline:
    """Election timeline model."""

    election_type: str
    region: str
    registration_start: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    nomination_date: Optional[datetime] = None
    campaign_start: Optional[datetime] = None
    polling_date: Optional[datetime] = None
    result_date: Optional[datetime] = None
    status: str = "upcoming"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class FAQ:
    """FAQ model."""

    question: str
    answer: str
    category: str
    language: str = "en"
    tags: list[str] = field(default_factory=list)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_published: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Reminder:
    """Reminder model."""

    user_id: str
    reminder_type: str
    title: str
    description: str = ""
    reminder_date: Optional[datetime] = None
    calendar_synced: bool = False
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Announcement:
    """Announcement model."""

    title: str
    message: str
    category: str
    priority: str = "medium"
    region: str = ""
    published_by: Optional[str] = None
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Bookmark:
    """Bookmark model."""

    user_id: str
    resource_type: str
    resource_id: str
    title: str
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class PollingGuidance:
    """Polling guidance model."""

    region: str
    title: str
    description: str = ""
    map_enabled: bool = False
    contact_info: dict[str, str] = field(default_factory=dict)
    help_links: list[dict[str, str]] = field(default_factory=list)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Analytics:
    """Analytics model."""

    metric_type: str
    metric_value: int
    date: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Setting:
    """Settings model."""

    key: str
    value: Any
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class VoterPreference:
    """Voter preference model."""

    user_id: str
    language: str = "en"
    notifications_enabled: bool = True
    calendar_sync_enabled: bool = False
    preferred_state: str = ""
    preferred_constituency: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


# Firestore Collection Names
class Collections:
    USERS = "users"
    ELECTION_PROCESS = "election_process"
    TIMELINES = "timelines"
    FAQS = "faqs"
    REMINDERS = "reminders"  # Subcollection under users
    ANNOUNCEMENTS = "announcements"
    BOOKMARKS = "bookmarks"  # Subcollection under users
    ANALYTICS = "analytics"
    POLLING_GUIDANCE = "polling_guidance"
    SETTINGS = "settings"


# Query indexes configuration (for firestore.indexes.json)
INDEXES = [
    {
        "collection": "faqs",
        "fields": [
            {"fieldPath": "category", "order": "ASC"},
            {"fieldPath": "language", "order": "ASC"},
            {"fieldPath": "is_published", "order": "DESC"},
        ],
    },
    {
        "collection": "timelines",
        "fields": [
            {"fieldPath": "election_type", "order": "ASC"},
            {"fieldPath": "region", "order": "ASC"},
            {"fieldPath": "polling_date", "order": "ASC"},
        ],
    },
    {
        "collection": "announcements",
        "fields": [
            {"fieldPath": "is_active", "order": "DESC"},
            {"fieldPath": "priority", "order": "DESC"},
            {"fieldPath": "published_at", "order": "DESC"},
        ],
    },
]
