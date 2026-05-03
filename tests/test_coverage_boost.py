"""Tests for uncovered modules to boost coverage to 85%+."""

from unittest.mock import MagicMock, patch


class TestErrorHandler:
    """Test error handler middleware."""

    def test_error_handler_404(self):
        from flask import Flask

        from middleware.error_handler import register_error_handlers

        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        with app.test_client() as client:
            response = client.get("/nonexistent-route")
            assert response.status_code == 404

    def test_error_handler_500(self):
        from flask import Flask

        from middleware.error_handler import register_error_handlers

        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        @app.route("/trigger-error")
        def trigger_error():
            raise RuntimeError("Test error")

        with app.test_client() as client:
            response = client.get("/trigger-error")
            assert response.status_code == 500


class TestRateLimiter:
    """Test rate limiter middleware."""

    def test_rate_limiter_init(self):
        from middleware.rate_limiter import RateLimiter

        limiter = RateLimiter()
        assert limiter._use_redis is False

    def test_rate_limiter_check_limit(self):
        from middleware.rate_limiter import RateLimiter

        limiter = RateLimiter()
        assert (
            limiter.check_limit("test_key", max_requests=5, window_seconds=60) is True
        )

    def test_rate_limiter_exceed_limit(self):
        from middleware.rate_limiter import RateLimiter

        limiter = RateLimiter()
        key = "rate_exceed_test"
        for _ in range(3):
            limiter.check_limit(key, max_requests=3, window_seconds=60)
        assert limiter.check_limit(key, max_requests=3, window_seconds=60) is False

    def test_rate_limiter_decorator(self):
        from flask import Flask

        from middleware.rate_limiter import rate_limit

        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.route("/limited")
        @rate_limit(max_requests=1, window_seconds=60)
        def limited():
            return "OK"

        with app.test_client() as client:
            res = client.get("/limited")
            assert res.status_code == 200
            res = client.get("/limited")
            assert res.status_code == 429

    def test_get_rate_limiter(self):
        from middleware.rate_limiter import RateLimiter, get_rate_limiter

        limiter = get_rate_limiter()
        assert isinstance(limiter, RateLimiter)


class TestDataModels:
    """Test data models."""

    def test_user_profile_model(self):
        from models.data_models import UserProfile

        user = UserProfile(
            uid="u1",
            email="test@test.com",
            full_name="Test User",
            role="voter",
        )
        assert user.uid == "u1"
        d = user.to_dict()
        assert d["uid"] == "u1"

    def test_reminder_model(self):
        from models.data_models import Reminder

        reminder = Reminder(
            user_id="u1",
            title="Test Reminder",
            reminder_type="election",
        )
        assert reminder.user_id == "u1"

    def test_faq_model(self):
        from models.data_models import FAQ

        faq = FAQ(
            question="What is voting?",
            answer="Voting is...",
            category="general",
        )
        assert faq.question == "What is voting?"

    def test_announcement_model(self):
        from models.data_models import Announcement

        ann = Announcement(
            title="Test",
            message="Message",
            category="news",
            priority="high",
        )
        assert ann.title == "Test"

    def test_polling_guidance_model(self):
        from models.data_models import PollingGuidance

        pg = PollingGuidance(
            title="Guide",
            region="Test Region",
        )
        assert pg.title == "Guide"

    def test_election_process_model(self):
        from models.data_models import ElectionProcess

        ep = ElectionProcess(
            title="How to Vote",
            category="general",
            intro="Introduction",
            steps=[],
        )
        assert ep.title == "How to Vote"

    def test_bookmark_model(self):
        from models.data_models import Bookmark

        bm = Bookmark(
            user_id="u1",
            resource_type="faq",
            resource_id="f1",
            title="Bookmark",
        )
        assert bm.user_id == "u1"

    def test_analytics_model(self):
        from models.data_models import Analytics

        ae = Analytics(
            metric_type="page_view",
            metric_value=100,
        )
        assert ae.metric_type == "page_view"

    def test_election_timeline_model(self):
        from models.data_models import ElectionTimeline

        tl = ElectionTimeline(
            election_type="general",
            region="Test",
        )
        assert tl.election_type == "general"


class TestGoogleServicesHub:
    """Test Google services hub."""

    def test_google_services_hub_imports(self):
        from services import google_services_hub

        assert hasattr(google_services_hub, "GoogleServicesHub")


class TestFirestoreValidation:
    """Test document ID validation."""

    def test_valid_id(self):
        from services.firestore_service import validate_document_id

        assert validate_document_id("valid_id_123") is True
        assert validate_document_id("test-id") is True

    def test_invalid_id(self):
        from services.firestore_service import validate_document_id

        assert validate_document_id("../etc/passwd") is False
        assert validate_document_id("path/traversal") is False
        assert validate_document_id("path\\traversal") is False
        assert validate_document_id(", ") is False


class TestConfigSecretKey:
    """Test config security."""

    def test_config_has_secret_key(self):
        from config import TestConfig

        assert TestConfig.SECRET_KEY is not None
        assert TestConfig.SECRET_KEY == "test-secret-key-for-testing-only"


class TestValidators:
    """Test validators module directly."""

    def test_validate_email_valid(self):
        from utils.validators import validate_email

        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False

    def test_validate_password(self):
        from utils.validators import validate_password

        assert validate_password("password123") is True
        assert validate_password("short") is False

    def test_sanitize_string(self):
        from utils.validators import sanitize_string

        result = sanitize_string("  hello world  ")
        assert result == "hello world"
        assert sanitize_string(", ") == ", "
        assert len(sanitize_string("x" * 2000, max_length=100)) <= 100


class TestConstants:
    """Test constants module."""

    def test_constants_exist(self):
        from utils import constants

        assert hasattr(constants, "SUPPORTED_LANGUAGES")
        assert hasattr(constants, "USER_ROLES")
        assert "voter" in constants.USER_ROLES
        assert "admin" in constants.USER_ROLES
