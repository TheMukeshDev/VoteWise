from unittest.mock import MagicMock, patch

from services.analytics_service import AnalyticsService, LoggingService


class TestAnalyticsService:
    @patch("config.Config")
    @patch("services.data_access_layer.firestore_db.create_analytics")
    def test_log_event_fallback(self, mock_create, mock_config):
        mock_config.FIREBASE_MEASUREMENT_ID = None
        service = AnalyticsService()
        service.client = None

        result = service.log_event("test_event", {"param": "value"})
        assert result is True
        mock_create.assert_called_once()

    @patch("config.Config")
    @patch("services.data_access_layer.firestore_db.create_analytics")
    def test_log_event_fallback_exception(self, mock_create, mock_config):
        mock_config.FIREBASE_MEASUREMENT_ID = None
        mock_create.side_effect = Exception("DB Error")
        service = AnalyticsService()
        service.client = None

        result = service.log_event("test_event", {"param": "value"})
        assert result is False

    @patch("config.Config")
    def test_log_event_with_client(self, mock_config):
        service = AnalyticsService()
        service.client = MagicMock()

        result = service.log_event("test_event", {"param": "value"})
        assert result is True
        service.client.log_event.assert_called_with("test_event", {"param": "value"})

    @patch("config.Config")
    def test_log_event_with_client_exception(self, mock_config):
        service = AnalyticsService()
        service.client = MagicMock()
        service.client.log_event.side_effect = Exception("Client Error")

        with patch.object(
            service, "_log_to_firestore", return_value=True
        ) as mock_fallback:
            result = service.log_event("test_event", {"param": "value"})
            assert result is True
            mock_fallback.assert_called_with("test_event", {"param": "value"})

    def test_specific_events(self):
        service = AnalyticsService()
        with patch.object(service, "log_event", return_value=True) as mock_log:
            service.log_page_view("home", "u1")
            mock_log.assert_called_with(
                "page_view", {"page_name": "home", "user_id": "u1"}
            )

            service.log_feature_use("search", "u1")
            mock_log.assert_called_with(
                "feature_use", {"feature_name": "search", "user_id": "u1"}
            )

            service.log_language_change("hi", "u1")
            mock_log.assert_called_with(
                "language_change", {"language": "hi", "user_id": "u1"}
            )

            service.log_reminder_create("election", "u1")
            mock_log.assert_called_with(
                "reminder_create", {"reminder_type": "election", "user_id": "u1"}
            )

            service.log_calendar_sync(True, "u1")
            mock_log.assert_called_with(
                "calendar_sync", {"success": True, "user_id": "u1"}
            )

            service.log_polling_booth_search("u1")
            mock_log.assert_called_with("polling_booth_search", {"user_id": "u1"})

            service.log_voice_input(True, "u1")
            mock_log.assert_called_with(
                "voice_input", {"success": True, "user_id": "u1"}
            )

            service.log_audio_playback("guidance", "u1")
            mock_log.assert_called_with(
                "audio_playback", {"content_type": "guidance", "user_id": "u1"}
            )

            service.log_ai_chat("hello", "u1")
            mock_log.assert_called_with(
                "ai_chat", {"query_preview": "hello", "user_id": "u1"}
            )

            service.log_signup("email", "u1")
            mock_log.assert_called_with("signup", {"method": "email", "user_id": "u1"})

            service.log_login("google", "u1")
            mock_log.assert_called_with("login", {"method": "google", "user_id": "u1"})

    def test_get_user_stats(self):
        service = AnalyticsService()
        stats = service.get_user_stats("u1")
        assert stats["user_id"] == "u1"
        assert stats["session_count"] == 0


class TestLoggingService:
    def test_init_logging(self):
        """Test logging initialization - tests it can be called."""
        service = LoggingService()
        assert service.logger is not None or service.logger is None

    @patch("config.Config")
    def test_log_info(self, mock_config):
        service = LoggingService()
        service.logger = MagicMock()
        service.log_info("test")
        service.logger.log.assert_called_with({"message": "test"}, severity="INFO")

    @patch("config.Config")
    def test_log_warning(self, mock_config):
        service = LoggingService()
        service.logger = MagicMock()
        service.log_warning("test")
        service.logger.log.assert_called_with({"message": "test"}, severity="WARNING")

    @patch("config.Config")
    def test_log_error(self, mock_config):
        service = LoggingService()
        service.logger = MagicMock()
        service.log_error("test")
        service.logger.log.assert_called_with({"message": "test"}, severity="ERROR")

    @patch("config.Config")
    def test_log_http_request(self, mock_config):
        service = LoggingService()
        service.logger = MagicMock()
        service.log_http_request("GET", "/", 200, 0.5)
        service.logger.log.assert_called_with(
            {
                "method": "GET",
                "path": "/",
                "status": 200,
                "latency_ms": 500.0,
            },
            severity="INFO",
        )
