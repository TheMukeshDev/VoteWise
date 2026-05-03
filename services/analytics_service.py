"""
Analytics Service for VoteWise AI

Provides analytics tracking using Firebase Analytics.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Firebase Analytics integration."""

    def __init__(self):
        self.measurement_id = None
        self._init_analytics()

    def _init_analytics(self):
        """Initialize Firebase Analytics."""
        try:
            from firebase_analytics import analytics as firebase_analytics

            from config import Config

            if Config.FIREBASE_MEASUREMENT_ID:
                self.measurement_id = Config.FIREBASE_MEASUREMENT_ID
                self.client = firebase_analytics
            else:
                self.client = None
        except (ImportError, RuntimeError):
            self.client = None

    def log_event(self, event_name: str, params: Optional[dict[str, Any]] = None) -> bool:
        """
        Log custom event.

        Args:
            event_name: Event name
            params: Event parameters

        Returns:
            True if logged
        """
        if self.client:
            try:
                self.client.log_event(event_name, params or {})
                return True
            except (RuntimeError, ConnectionError, ValueError):
                pass

        return self._log_to_firestore(event_name, params)

    def log_page_view(self, page_name: str, user_id: Optional[str] = None) -> bool:
        """Log page view."""
        return self.log_event("page_view", {"page_name": page_name, "user_id": user_id or "anonymous"})

    def log_feature_use(self, feature_name: str, user_id: str) -> bool:
        """Log feature usage."""
        return self.log_event("feature_use", {"feature_name": feature_name, "user_id": user_id})

    def log_language_change(self, language: str, user_id: str) -> bool:
        """Log language preference change."""
        return self.log_event("language_change", {"language": language, "user_id": user_id})

    def log_reminder_create(self, reminder_type: str, user_id: str) -> bool:
        """Log reminder creation."""
        return self.log_event("reminder_create", {"reminder_type": reminder_type, "user_id": user_id})

    def log_calendar_sync(self, success: bool, user_id: str) -> bool:
        """Log calendar sync attempt."""
        return self.log_event("calendar_sync", {"success": success, "user_id": user_id})

    def log_polling_booth_search(self, user_id: str) -> bool:
        """Log polling booth search."""
        return self.log_event("polling_booth_search", {"user_id": user_id})

    def log_voice_input(self, success: bool, user_id: str) -> bool:
        """Log voice input usage."""
        return self.log_event("voice_input", {"success": success, "user_id": user_id})

    def log_audio_playback(self, content_type: str, user_id: str) -> bool:
        """Log audio playback."""
        return self.log_event("audio_playback", {"content_type": content_type, "user_id": user_id})

    def log_ai_chat(self, query: str, user_id: str) -> bool:
        """Log AI chat interaction."""
        return self.log_event("ai_chat", {"query_preview": query[:50], "user_id": user_id})

    def log_signup(self, method: str, user_id: str) -> bool:
        """Log user signup."""
        return self.log_event("signup", {"method": method, "user_id": user_id})

    def log_login(self, method: str, user_id: str) -> bool:
        """Log user login."""
        return self.log_event("login", {"method": method, "user_id": user_id})

    def _log_to_firestore(self, event_name: str, params: Optional[dict]) -> bool:
        """Fallback logging to Firestore."""
        try:
            from datetime import datetime

            from services.data_access_layer import firestore_db

            doc_id = f"{event_name}_{datetime.now().timestamp()}"
            data = {
                "event_name": event_name,
                "params": params or {},
                "timestamp": datetime.now().isoformat(),
            }
            firestore_db.create_analytics(doc_id, data)
            return True
        except (RuntimeError, ConnectionError, ValueError):
            return False

    def get_user_stats(self, user_id: str) -> dict[str, Any]:
        """Get user statistics."""
        return {
            "user_id": user_id,
            "session_count": 0,
            "feature_usage": {},
            "language": "en",
        }


class LoggingService:
    """Cloud Logging integration."""

    def __init__(self):
        self._initialized = False
        self._init_logging()

    def _init_logging(self):
        """Initialize Cloud Logging."""
        try:
            from google.cloud import logging as cloud_logging

            from config import Config

            if Config.FIREBASE_ADMIN_JSON:
                self.client = cloud_logging.Client()
                self.logger = self.client.logger("votewise-ai")
                self._initialized = True
            else:
                self.client = None
                self.logger = None
        except (RuntimeError, ConnectionError, ValueError) as e:
            logger.warning("Failed to initialize Cloud Logging: %s", e)
            self.client = None
            self.logger = None

    def log_info(self, message: str, **kwargs) -> None:
        """Log info message."""
        if self.logger:
            try:
                self.logger.log({"message": message, **kwargs}, severity="INFO")
            except (RuntimeError, ConnectionError, ValueError):
                pass
        logger.info(message)

    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        if self.logger:
            try:
                self.logger.log({"message": message, **kwargs}, severity="WARNING")
            except (RuntimeError, ConnectionError, ValueError):
                pass
        logger.warning(message)

    def log_error(self, message: str, **kwargs) -> None:
        """Log error message."""
        if self.logger:
            try:
                self.logger.log({"message": message, **kwargs}, severity="ERROR")
            except (RuntimeError, ConnectionError, ValueError):
                pass
        logger.error(message)

    def log_http_request(self, method: str, path: str, status: int, latency: float) -> None:
        """Log HTTP request."""
        if self.logger:
            try:
                self.logger.log(
                    {
                        "method": method,
                        "path": path,
                        "status": status,
                        "latency_ms": latency * 1000,
                    },
                    severity="INFO",
                )
            except (RuntimeError, ConnectionError, ValueError):
                pass


analytics_service = AnalyticsService()
logging_service = LoggingService()
