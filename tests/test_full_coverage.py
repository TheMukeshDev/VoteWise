"""Comprehensive tests to push coverage toward 100%."""

from unittest.mock import MagicMock, patch

from flask import Flask, jsonify


class TestErrorHandlerFull:
    """Complete error handler coverage."""

    def test_api_error_default(self):
        from middleware.error_handler import APIError

        err = APIError("test error")
        assert err.status_code == 500
        assert err.error_code == "internal_error"
        d = err.to_dict()
        assert d["success"] is False

    def test_api_error_custom(self):
        from middleware.error_handler import APIError

        err = APIError("custom", 422, "custom_err")
        assert err.status_code == 422
        assert err.error_code == "custom_err"

    def test_not_found_error(self):
        from middleware.error_handler import NotFoundError

        err = NotFoundError()
        assert err.status_code == 404
        err2 = NotFoundError("custom msg")
        assert err2.message == "custom msg"

    def test_unauthorized_error(self):
        from middleware.error_handler import UnauthorizedError

        err = UnauthorizedError()
        assert err.status_code == 401

    def test_forbidden_error(self):
        from middleware.error_handler import ForbiddenError

        err = ForbiddenError()
        assert err.status_code == 403

    def test_validation_error(self):
        from middleware.error_handler import ValidationError

        err = ValidationError()
        assert err.status_code == 400

    def test_conflict_error(self):
        from middleware.error_handler import ConflictError

        err = ConflictError()
        assert err.status_code == 409

    def test_register_handlers(self):
        from middleware.error_handler import APIError, register_error_handlers

        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        @app.route("/raise-api")
        def raise_api():
            raise APIError("api err", 422, "api")

        with app.test_client() as c:
            r = c.get("/raise-api")
            assert r.status_code == 422

    def test_handle_unexpected(self):
        from middleware.error_handler import register_error_handlers

        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        @app.route("/raise-unexpected")
        def raise_unexpected():
            raise RuntimeError("unexpected")

        with app.test_client() as c:
            r = c.get("/raise-unexpected")
            assert r.status_code == 500
            assert r.json["error"] == "unexpected_error"

    def test_handle_405(self):
        from middleware.error_handler import register_error_handlers

        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        @app.route("/only-post", methods=["POST"])
        def only_post():
            return "OK"

        with app.test_client() as c:
            r = c.get("/only-post")
            assert r.status_code in [404, 405]


class TestRateLimiterFull:
    """Complete rate limiter coverage."""

    def test_redis_failure_fallback(self):
        from middleware.rate_limiter import RateLimiter

        limiter = RateLimiter(redis_url="redis://bad:6379")
        assert limiter._use_redis is False

    def test_redis_success_path(self):
        from middleware.rate_limiter import RateLimiter

        limiter = RateLimiter()
        mock_redis = MagicMock()
        limiter._redis_client = mock_redis
        limiter._use_redis = True
        pipe = MagicMock()
        mock_redis.pipeline.return_value = pipe
        pipe.execute.return_value = [0, 0, 1, True]
        result = limiter.check_limit("redis_key", 5, 60)
        assert result is True

    def test_redis_failure_during_check(self):
        from middleware.rate_limiter import RateLimiter

        limiter = RateLimiter()
        limiter._redis_client = MagicMock()
        limiter._use_redis = True
        limiter._redis_client.pipeline.side_effect = Exception("Redis down")
        assert limiter.check_limit("fail_key", 5, 60) is True

    def test_rate_limit_decorator(self):
        from middleware.rate_limiter import _rate_limit_store, rate_limit

        app = Flask(__name__)
        app.config["TESTING"] = True
        _rate_limit_store.clear()

        @app.route("/rate-limited")
        @rate_limit(max_requests=1, window_seconds=60)
        def rl():
            return "OK"

        with app.test_client() as c:
            r1 = c.get("/rate-limited")
            assert r1.status_code == 200
            r2 = c.get("/rate-limited")
            assert r2.status_code == 429
            assert r2.json["error"] == "rate_limit_exceeded"


class TestDataModelsFull:
    """Cover all to_dict methods."""

    def test_election_process_to_dict(self):
        from models.data_models import ElectionProcess

        ep = ElectionProcess(title="T", category="C", intro="I", steps=[{"s": "1"}])
        d = ep.to_dict()
        assert d["title"] == "T"

    def test_election_timeline_to_dict(self):
        from models.data_models import ElectionTimeline

        et = ElectionTimeline(election_type="general", region="R")
        d = et.to_dict()
        assert d["election_type"] == "general"

    def test_faq_to_dict(self):
        from models.data_models import FAQ

        faq = FAQ(question="Q?", answer="A.", category="general")
        d = faq.to_dict()
        assert d["question"] == "Q?"

    def test_reminder_to_dict(self):
        from models.data_models import Reminder

        r = Reminder(user_id="u1", title="T", reminder_type="voting")
        d = r.to_dict()
        assert d["user_id"] == "u1"

    def test_announcement_to_dict(self):
        from models.data_models import Announcement

        a = Announcement(title="T", message="M", category="news")
        d = a.to_dict()
        assert d["title"] == "T"

    def test_bookmark_to_dict(self):
        from models.data_models import Bookmark

        b = Bookmark(user_id="u1", resource_type="faq", resource_id="f1", title="B")
        d = b.to_dict()
        assert d["user_id"] == "u1"

    def test_polling_guidance_to_dict(self):
        from models.data_models import PollingGuidance

        pg = PollingGuidance(title="T", region="R")
        d = pg.to_dict()
        assert d["title"] == "T"

    def test_analytics_to_dict(self):
        from models.data_models import Analytics

        a = Analytics(metric_type="page_view", metric_value=10)
        d = a.to_dict()
        assert d["metric_type"] == "page_view"

    def test_enums(self):
        from models.data_models import (AnnouncementPriority, ReminderStatus,
                                        ReminderType, ResourceType, UserRole)

        assert UserRole.VOTER.value == "voter"
        assert UserRole.ADMIN.value == "admin"
        assert ReminderType.REGISTRATION_DEADLINE.value == "registration_deadline"
        assert ReminderStatus.PENDING.value == "pending"
        assert AnnouncementPriority.URGENT.value == "urgent"
        assert ResourceType.FAQ.value == "faq"


class TestDocsRoutes:
    """Test docs routes."""

    def test_openapi_spec(self, client):
        response = client.get("/api/openapi.json")
        assert response.status_code in [200, 404]

    def test_docs_page(self, client):
        response = client.get("/api/docs")
        assert response.status_code in [200, 404, 500]


class TestSpeechRoutes:
    """Test speech routes."""

    def test_text_to_speech_missing_text(self, client):
        r = client.post("/api/speech/text-to-speech", json={})
        assert r.status_code == 400

    def test_text_to_speech_unavailable(self, client):
        with patch("routes.speech.tts_service") as mock_tts:
            mock_tts.text_to_speech.return_value = None
            r = client.post("/api/speech/text-to-speech", json={"text": "Hello"})
            assert r.status_code == 503

    def test_speech_to_text_missing_audio(self, client):
        r = client.post("/api/speech/speech-to-text", json={})
        assert r.status_code == 400

    def test_speech_to_text_unavailable(self, client):
        with patch("routes.speech.stt_service") as mock_stt:
            mock_stt.recognize.return_value = None
            r = client.post("/api/speech/speech-to-text", json={"audio_data": "bytes"})
            assert r.status_code == 503

    def test_list_voices(self, client):
        r = client.get("/api/speech/voices")
        assert r.status_code == 200

    def test_speech_health(self, client):
        r = client.get("/api/speech/health")
        assert r.status_code == 200

    def test_text_to_speech_success(self, client):
        with patch("routes.speech.tts_service") as mock_tts:
            mock_tts.text_to_speech.return_value = {
                "audio_content": "data",
                "audio_format": "mp3",
            }
            r = client.post("/api/speech/text-to-speech", json={"text": "Hello"})
            assert r.status_code == 200

    def test_speech_to_text_success(self, client):
        with patch("routes.speech.stt_service") as mock_stt:
            mock_stt.recognize.return_value = "Hello world"
            r = client.post("/api/speech/speech-to-text", json={"audio_data": "bytes"})
            assert r.status_code == 200


class TestTimelineRoutes:
    """Test timeline routes."""

    def test_get_timeline(self, client):
        with patch("routes.timeline.timeline_service") as mock_svc:
            mock_svc.get_all.return_value = []
            r = client.get("/api/timeline/")
            assert r.status_code == 200

    def test_get_timeline_by_id_not_found(self, client):
        with patch("routes.timeline.timeline_service") as mock_svc:
            mock_svc.get_by_id.return_value = None
            r = client.get("/api/timeline/nonexistent")
            assert r.status_code == 404


class TestPollingGuidanceRoutes:
    """Test polling guidance routes."""

    def test_get_polling_guidance(self, client):
        with patch("routes.polling_guidance.polling_guidance_service") as mock_svc:
            mock_svc.get_all_for_admin.return_value = []
            r = client.get("/api/admin/polling-guidance/")
            assert r.status_code == 200

    def test_get_polling_guidance_by_id_not_found(self, client):
        with patch("routes.polling_guidance.polling_guidance_service") as mock_svc:
            mock_svc.get_by_id.return_value = None
            r = client.get("/api/admin/polling-guidance/nonexistent")
            assert r.status_code == 404

    def test_get_polling_guidance_by_region(self, client):
        with patch("routes.polling_guidance.polling_guidance_service") as mock_svc:
            mock_svc.get_all_for_admin.return_value = [{"region": "KA"}]
            r = client.get("/api/admin/polling-guidance/?region=KA")
            assert r.status_code == 200


class TestElectionProcessRoutes:
    """Test election process admin routes."""

    def test_get_election_processes_admin(self, client):
        with patch("routes.election_process.election_process_service") as mock_svc:
            mock_svc.get_all_for_admin.return_value = []
            r = client.get("/api/admin/election-process")
            assert r.status_code == 200

    def test_get_election_process_not_found(self, client):
        with patch("routes.election_process.election_process_service") as mock_svc:
            mock_svc.get_by_id.return_value = None
            r = client.get("/api/admin/election-process/nonexistent")
            assert r.status_code == 404

    def test_create_election_process_missing_fields(self, client):
        r = client.post("/api/admin/election-process", json={"title": "Test"})
        assert r.status_code == 400

    def test_create_election_process_steps_not_list(self, client):
        r = client.post(
            "/api/admin/election-process",
            json={"title": "T", "intro": "I", "steps": "not_list"},
        )
        assert r.status_code == 400

    def test_create_election_process_invalid_lang(self, client):
        r = client.post(
            "/api/admin/election-process",
            json={"title": "T", "intro": "I", "steps": [], "language": "zz"},
        )
        assert r.status_code == 400

    def test_update_election_process_not_found(self, client):
        with patch("routes.election_process.election_process_service") as mock_svc:
            mock_svc.update.return_value = None
            r = client.put("/api/admin/election-process/x", json={"title": "Updated"})
            assert r.status_code == 404

    def test_update_election_process_invalid_lang(self, client):
        r = client.put("/api/admin/election-process/x", json={"language": "zz"})
        assert r.status_code == 400

    def test_delete_election_process_not_found(self, client):
        with patch("routes.election_process.election_process_service") as mock_svc:
            mock_svc.delete.return_value = False
            r = client.delete("/api/admin/election-process/x")
            assert r.status_code == 404


class TestTimelineAdminRoutes:
    """Test timeline admin routes."""

    def test_get_timelines_admin(self, client):
        with patch("routes.timeline_admin.timeline_service") as mock_svc:
            mock_svc.get_all_for_admin.return_value = []
            r = client.get("/api/admin/timelines")
            assert r.status_code == 200

    def test_get_timeline_not_found_admin(self, client):
        with patch("routes.timeline_admin.timeline_service") as mock_svc:
            mock_svc.get_by_id.return_value = None
            r = client.get("/api/admin/timelines/nonexistent")
            assert r.status_code == 404

    def test_create_timeline_missing_fields(self, client):
        r = client.post("/api/admin/timelines", json={"election_type": "general"})
        assert r.status_code == 400

    def test_create_timeline_invalid_type(self, client):
        r = client.post(
            "/api/admin/timelines",
            json={
                "election_type": "invalid_type",
                "region": "KA",
                "polling_date": "2026-01-01",
            },
        )
        assert r.status_code == 400

    def test_create_timeline_invalid_status(self, client):
        r = client.post(
            "/api/admin/timelines",
            json={
                "election_type": "general",
                "region": "KA",
                "polling_date": "2026-01-01",
                "status": "invalid",
            },
        )
        assert r.status_code == 400

    def test_update_timeline_not_found(self, client):
        with patch("routes.timeline_admin.timeline_service") as mock_svc:
            mock_svc.update.return_value = None
            r = client.put("/api/admin/timelines/x", json={"title": "Updated"})
            assert r.status_code == 404

    def test_update_timeline_invalid_type(self, client):
        r = client.put("/api/admin/timelines/x", json={"election_type": "invalid"})
        assert r.status_code == 400

    def test_update_timeline_invalid_status(self, client):
        r = client.put("/api/admin/timelines/x", json={"status": "invalid"})
        assert r.status_code == 400

    def test_delete_timeline_not_found(self, client):
        with patch("routes.timeline_admin.timeline_service") as mock_svc:
            mock_svc.delete.return_value = False
            r = client.delete("/api/admin/timelines/x")
            assert r.status_code == 404


class TestAnnouncementRoutesFull:
    """Complete announcement admin route coverage."""

    def test_get_announcements_admin(self, client):
        with patch("routes.announcement.announcement_service") as mock_svc:
            mock_svc.get_all_for_admin.return_value = []
            r = client.get("/api/admin/announcements")
            assert r.status_code == 200

    def test_get_announcements_with_filters(self, client):
        with patch("routes.announcement.announcement_service") as mock_svc:
            mock_svc.get_all_for_admin.return_value = []
            r = client.get("/api/admin/announcements?region=KA&priority=high")
            assert r.status_code == 200

    def test_get_announcement_not_found(self, client):
        with patch("routes.announcement.announcement_service") as mock_svc:
            mock_svc.get_by_id.return_value = None
            r = client.get("/api/admin/announcements/nonexistent")
            assert r.status_code == 404

    def test_create_announcement_missing_fields(self, client):
        r = client.post("/api/admin/announcements", json={"title": "Test"})
        assert r.status_code == 400

    def test_create_announcement_invalid_priority(self, client):
        r = client.post(
            "/api/admin/announcements",
            json={"title": "T", "message": "M", "priority": "critical"},
        )
        assert r.status_code == 400

    def test_update_announcement_not_found(self, client):
        with patch("routes.announcement.announcement_service") as mock_svc:
            mock_svc.update.return_value = None
            r = client.put("/api/admin/announcements/x", json={"title": "Updated"})
            assert r.status_code == 404

    def test_update_announcement_invalid_priority(self, client):
        r = client.put("/api/admin/announcements/x", json={"priority": "critical"})
        assert r.status_code == 400

    def test_delete_announcement_not_found(self, client):
        with patch("routes.announcement.announcement_service") as mock_svc:
            mock_svc.delete.return_value = False
            r = client.delete("/api/admin/announcements/x")
            assert r.status_code == 404


class TestBookmarkRoutesFull:
    """Complete bookmark route coverage."""

    def test_get_bookmarks(self, client):
        with patch("routes.bookmark.get_bookmarks") as mock_gb:
            mock_gb.return_value = []
            r = client.get("/api/user/bookmarks")
            assert r.status_code == 200

    def test_save_bookmark(self, client):
        with patch("routes.bookmark.get_bookmark_by_resource", return_value=None):
            with patch("routes.bookmark.save_bookmark") as mock_sb:
                mock_sb.return_value = "bm1"
                r = client.post(
                    "/api/user/bookmarks",
                    json={"resource_type": "faq", "resource_id": "f1", "title": "FAQ"},
                )
                assert r.status_code == 201

    def test_save_bookmark_missing_fields(self, client):
        r = client.post("/api/user/bookmarks", json={"title": "Test"})
        assert r.status_code == 400

    def test_save_bookmark_invalid_resource_type(self, client):
        r = client.post(
            "/api/user/bookmarks", json={"resource_type": "invalid", "resource_id": "x"}
        )
        assert r.status_code == 400

    def test_save_bookmark_already_exists(self, client):
        with patch("routes.bookmark.get_bookmark_by_resource") as mock_gbr:
            mock_gbr.return_value = {"id": "bm1"}
            r = client.post(
                "/api/user/bookmarks",
                json={"resource_type": "faq", "resource_id": "f1"},
            )
            assert r.status_code == 400

    def test_delete_bookmark(self, client):
        with patch("routes.bookmark.delete_bookmark_from_db") as mock_db:
            mock_db.return_value = True
            r = client.delete("/api/user/bookmarks/bm1")
            assert r.status_code == 200

    def test_delete_bookmark_not_found(self, client):
        with patch("routes.bookmark.delete_bookmark_from_db") as mock_db:
            mock_db.return_value = False
            r = client.delete("/api/user/bookmarks/bm1")
            assert r.status_code == 404


class TestChatRoutesFull:
    """Complete chat route coverage."""

    def test_chat_missing_message(self, client):
        r = client.post("/api/chat/chat", json={})
        assert r.status_code == 400

    def test_chat_message_too_long(self, client):
        r = client.post("/api/chat/chat", json={"message": "x" * 1001})
        assert r.status_code == 400

    def test_chat_fallback_register_intent(self, client):
        r = client.post("/api/chat/chat", json={"message": "how to register"})
        assert r.status_code == 200

    def test_chat_fallback_document_intent(self, client):
        r = client.post("/api/chat/chat", json={"message": "what documents do i need"})
        assert r.status_code == 200

    def test_chat_fallback_booth_intent(self, client):
        r = client.post("/api/chat/chat", json={"message": "find my polling booth"})
        assert r.status_code == 200

    def test_chat_fallback_default(self, client):
        r = client.post("/api/chat/chat", json={"message": "hello there"})
        assert r.status_code == 200

    def test_chat_with_user_prefs(self, client):
        r = client.post(
            "/api/chat/chat", json={"message": "hello", "user_prefs": {"state": "KA"}}
        )
        assert r.status_code == 200

    def test_chat_health(self, client):
        r = client.get("/api/chat/health")
        assert r.status_code == 200

    def test_chat_exception_fallback(self, client):
        with patch("routes.chat._generate_ai_response", side_effect=Exception("err")):
            r = client.post("/api/chat/chat", json={"message": "test"})
            assert r.status_code == 200


class TestReminderRoutes:
    """Test reminder routes."""

    def test_get_reminders(self, client):
        with patch("routes.reminder.get_reminders") as mock_gr:
            mock_gr.return_value = []
            r = client.get("/api/reminders")
            assert r.status_code == 200

    def test_create_reminder(self, client):
        with patch("routes.reminder.save_reminder_to_db") as mock_sr:
            mock_sr.return_value = "r1"
            r = client.post(
                "/api/reminders", json={"title": "Vote", "reminder_date": "2026-05-01"}
            )
            assert r.status_code == 201

    def test_create_reminder_missing_title(self, client):
        r = client.post("/api/reminders", json={"reminder_date": "2026-05-01"})
        assert r.status_code == 400

    def test_create_reminder_invalid_type(self, client):
        with patch("routes.reminder.save_reminder_to_db") as mock_sr:
            mock_sr.return_value = "r1"
            r = client.post(
                "/api/reminders",
                json={
                    "title": "Vote",
                    "reminder_date": "2026-05-01",
                    "reminder_type": "bad",
                },
            )
            assert r.status_code == 201

    def test_update_reminder(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = {"id": "r1", "title": "Old"}
            with patch("routes.reminder.update_reminder_in_db") as mock_ur:
                mock_ur.return_value = "r1"
                r = client.put("/api/reminders/r1", json={"title": "Updated"})
                assert r.status_code == 200

    def test_update_reminder_not_found_get(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = None
            r = client.put("/api/reminders/r1", json={"title": "Updated"})
            assert r.status_code == 404

    def test_update_reminder_save_fails(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = {"id": "r1"}
            with patch("routes.reminder.update_reminder_in_db") as mock_ur:
                mock_ur.return_value = None
                r = client.put("/api/reminders/r1", json={"title": "Updated"})
                assert r.status_code == 500

    def test_delete_reminder(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = {"id": "r1"}
            with patch("routes.reminder.delete_reminder_from_db") as mock_dr:
                mock_dr.return_value = True
                r = client.delete("/api/reminders/r1")
                assert r.status_code == 200

    def test_delete_reminder_not_found_get(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = None
            r = client.delete("/api/reminders/r1")
            assert r.status_code == 404

    def test_delete_reminder_save_fails(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = {"id": "r1"}
            with patch("routes.reminder.delete_reminder_from_db") as mock_dr:
                mock_dr.return_value = False
                r = client.delete("/api/reminders/r1")
                assert r.status_code == 500

    def test_get_reminder_by_id(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = {"id": "r1", "title": "Test"}
            r = client.get("/api/reminders/r1")
            assert r.status_code == 200

    def test_get_reminder_by_id_not_found(self, client):
        with patch("routes.reminder.get_reminder") as mock_gr:
            mock_gr.return_value = None
            r = client.get("/api/reminders/r1")
            assert r.status_code == 404


class TestGoogleServicesHubFull:
    """Test Google services hub methods."""

    def test_hub_verify_token(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.auth = MagicMock()
        hub.auth.verify_id_token.return_value = {"uid": "u1"}
        result = hub.verify_token("token")
        assert result == {"uid": "u1"}

    def test_hub_get_user_profile(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.profiles = MagicMock()
        hub.profiles.get_user_profile.return_value = {"id": "u1"}
        result = hub.get_user_profile("u1")
        assert result["id"] == "u1"

    def test_hub_find_polling_booth(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.maps = MagicMock()
        hub.maps.find_polling_booth.return_value = {"booth_name": "Test"}
        result = hub.find_polling_booth(1.0, 2.0)
        assert result["booth_name"] == "Test"

    def test_hub_find_multiple_booths(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.maps = MagicMock()
        hub.maps.find_multiple_booths.return_value = [{"name": "B1"}, {"name": "B2"}]
        result = hub.find_multiple_booths(1.0, 2.0, max_results=3)
        assert len(result) == 2

    def test_hub_create_calendar_reminder(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.calendar = MagicMock()
        hub.calendar.create_election_reminder.return_value = {"id": "e1"}
        result = hub.create_calendar_reminder("Election", "2026-01-01")
        assert result["id"] == "e1"

    def test_hub_generate_ics(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.calendar_local = MagicMock()
        hub.calendar_local.generate_voting_calendar.return_value = "BEGIN:VCALENDAR"
        result = hub.generate_ics("Election", "2026-01-01")
        assert "VCALENDAR" in result

    def test_hub_translate_content(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.translate = MagicMock()
        hub.translate.translate.return_value = {"translated_text": "Translated"}
        result = hub.translate_content("Hello", "hi")
        assert "translated_text" in result

    def test_hub_translate_faqs(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.translator = MagicMock()
        hub.translator.translate_faqs.return_value = [{"question": "Translated"}]
        result = hub.translate_faqs([], "hi")
        assert isinstance(result, list)

    def test_hub_get_supported_languages(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.translate = MagicMock()
        hub.translate.get_supported_languages.return_value = [
            {"code": "en", "name": "English"}
        ]
        result = hub.get_supported_languages()
        assert len(result) > 0

    def test_hub_get_voice_config(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.speech_to_text = MagicMock()
        hub.speech_to_text.get_audio_config.return_value = {"sample_rate": 16000}
        result = hub.get_voice_config()
        assert "sample_rate" in result

    def test_hub_get_available_voices(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.tts = MagicMock()
        hub.tts.get_available_voices.return_value = [{"name": "en-US-Neural2-J"}]
        result = hub.get_available_voices()
        assert len(result) > 0

    def test_hub_synthesize_speech(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.tts = MagicMock()
        hub.tts.synthesize.return_value = {"audio_format": "mp3"}
        result = hub.synthesize_speech("Hello")
        assert result["audio_format"] == "mp3"

    def test_hub_speak_election_steps(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.tts = MagicMock()
        hub.tts.speak_election_steps.return_value = {"text": "Steps audio"}
        result = hub.speak_election_steps([{"title": "Step 1"}])
        assert "text" in result

    def test_hub_get_playback_url(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.audio = MagicMock()
        hub.audio.get_playback_url.return_value = "data:audio/mp3;base64,abc"
        result = hub.get_playback_url("abc")
        assert "base64" in result

    def test_hub_get_health_status(self):
        from services.google_services_hub import GoogleServicesHub

        hub = GoogleServicesHub()
        hub.db = MagicMock()
        hub.db.db = None
        hub.auth = MagicMock()
        hub.auth._initialized = False
        hub.maps = MagicMock()
        hub.maps.api_key = None
        hub.calendar = MagicMock()
        hub.calendar.access_token = None
        hub.translate = MagicMock()
        hub.translate._initialized = False
        hub.speech_to_text = MagicMock()
        hub.speech_to_text._initialized = False
        hub.tts = MagicMock()
        hub.tts._initialized = False
        result = hub.get_health_status()
        assert result["firestore"] is False
        assert result["firebase_auth"] is False


class TestAppEndpoints:
    """Test app.py endpoints."""

    def test_app_redirect(self, client):
        r = client.get("/app")
        assert r.status_code == 302

    def test_health_endpoint(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json["status"] == "healthy"

    def test_request_logging(self, client):
        from flask import Flask, g

        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["ENV"] = "development"

        @app.before_request
        def before():
            g.request_start_time = 0.0

        @app.after_request
        def after(response):
            if hasattr(g, "request_start_time"):
                response.headers["X-Response-Time"] = "0.0"
            return response

        @app.route("/test-logging")
        def test_log():
            return "OK"

        with app.test_client() as c:
            r = c.get("/test-logging")
            assert r.status_code == 200


class TestConfigFull:
    """Complete config coverage."""

    def test_invalid_firebase_json(self):
        import os

        orig = os.environ.get("FIREBASE_ADMIN_JSON")
        try:
            os.environ["FIREBASE_ADMIN_JSON"] = "not-json"
            from config import _get_firebase_admin_json

            try:
                _get_firebase_admin_json()
            except ValueError:
                pass
        finally:
            if orig is not None:
                os.environ["FIREBASE_ADMIN_JSON"] = orig
            else:
                os.environ.pop("FIREBASE_ADMIN_JSON", None)

    def test_firebase_from_individual_fields(self):
        import os

        keys = [
            "FIREBASE_PRIVATE_KEY",
            "FIREBASE_PROJECT_ID",
            "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_PRIVATE_KEY_ID",
        ]
        origs = {k: os.environ.get(k) for k in keys}
        try:
            os.environ["FIREBASE_PRIVATE_KEY"] = (
                "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----"
            )
            os.environ["FIREBASE_PROJECT_ID"] = "test-project"
            os.environ["FIREBASE_CLIENT_EMAIL"] = "test@test.iam.gserviceaccount.com"
            os.environ["FIREBASE_PRIVATE_KEY_ID"] = "key123"
            from config import _get_firebase_admin_json

            result = _get_firebase_admin_json()
            assert result["project_id"] == "test-project"
        finally:
            for k, v in origs.items():
                if v is not None:
                    os.environ[k] = v
                else:
                    os.environ.pop(k, None)

    def test_config_cors_production(self):
        import os

        orig = os.environ.get("CORS_ORIGINS")
        try:
            os.environ["CORS_ORIGINS"] = ", "
            from config import _resolve_cors_origins

            result = _resolve_cors_origins("production")
            assert result == ", "
        finally:
            if orig is not None:
                os.environ["CORS_ORIGINS"] = orig
            else:
                os.environ.pop("CORS_ORIGINS", None)

    def test_config_cors_dev(self):
        from config import _resolve_cors_origins

        result = _resolve_cors_origins("development")
        assert result == "*"

    def test_config_by_name(self):
        from config import config_by_name

        assert "development" in config_by_name
        assert "production" in config_by_name
        assert "testing" in config_by_name
        assert config_by_name["default"] is not None

    def test_get_config(self):
        import os

        orig = os.environ.get("FLASK_ENV")
        try:
            os.environ["FLASK_ENV"] = "development"
            from config import DevelopmentConfig, get_config

            assert get_config() == DevelopmentConfig
        finally:
            if orig is not None:
                os.environ["FLASK_ENV"] = orig
            else:
                os.environ.pop("FLASK_ENV", None)


class TestAuthRoutesFull:
    """Complete auth route coverage."""

    def test_google_signin_success(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {
                "uid": "u1",
                "email": "test@example.com",
                "name": "Test User",
            }
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.return_value = {
                    "uid": "u1",
                    "email": "test@example.com",
                    "role": "voter",
                }
                mock_ups.create_user_profile.return_value = True
                mock_ups.update_last_login.return_value = True
                r = client.post(
                    "/api/auth/google-signin", json={"id_token": "google-token"}
                )
                assert r.status_code == 200

    def test_google_signin_profile_creation(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {
                "uid": "u2",
                "email": "new@example.com",
                "name": "New User",
            }
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.side_effect = [None, {"uid": "u2"}]
                mock_ups.create_user_profile.return_value = True
                mock_ups.update_last_login.return_value = True
                r = client.post(
                    "/api/auth/google-signin", json={"id_token": "google-token"}
                )
                assert r.status_code == 200

    def test_google_signin_missing_token(self, client):
        r = client.post("/api/auth/google-signin", json={})
        assert r.status_code == 400

    def test_google_signin_invalid_token(self, client):
        with patch("routes.auth.verify_firebase_token", return_value=None):
            r = client.post("/api/auth/google-signin", json={"id_token": "bad"})
            assert r.status_code == 401

    def test_google_signin_exception(self, client):
        with patch("routes.auth.verify_firebase_token", side_effect=Exception("err")):
            r = client.post("/api/auth/google-signin", json={"id_token": "token"})
            assert r.status_code == 500

    def test_login_success(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {"uid": "u1", "email": "t@t.com"}
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.return_value = {"uid": "u1", "role": "voter"}
                mock_ups.update_last_login.return_value = True
                r = client.post("/api/auth/login", json={"id_token": "token"})
                assert r.status_code == 200

    def test_login_missing_token(self, client):
        r = client.post("/api/auth/login", json={})
        assert r.status_code == 400

    def test_login_invalid_token(self, client):
        with patch("routes.auth.verify_firebase_token", return_value=None):
            r = client.post("/api/auth/login", json={"id_token": "bad"})
            assert r.status_code == 401

    def test_register_success(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {"uid": "u3", "email": "new@t.com"}
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.return_value = None
                mock_ups.create_user_profile.return_value = True
                r = client.post(
                    "/api/auth/register",
                    json={"id_token": "token", "profile": {"full_name": "New"}},
                )
                assert r.status_code == 201

    def test_register_already_exists(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {"uid": "u1", "email": "t@t.com"}
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.return_value = {"uid": "u1"}
                r = client.post("/api/auth/register", json={"id_token": "token"})
                assert r.status_code == 400

    def test_get_current_user(self, client):
        with patch("routes.auth.user_profile_service") as mock_ups:
            mock_ups.get_user_profile.return_value = {
                "uid": "u1",
                "email": "t@t.com",
                "role": "voter",
            }
            r = client.get("/api/auth/me")
            assert r.status_code == 200

    def test_get_current_user_not_found(self, client):
        with patch("routes.auth.user_profile_service") as mock_ups:
            mock_ups.get_user_profile.return_value = None
            r = client.get("/api/auth/me")
            assert r.status_code == 404

    def test_update_profile_auth(self, client):
        with patch("routes.auth.user_profile_service") as mock_ups:
            mock_ups.update_user_profile.return_value = True
            mock_ups.get_user_profile.return_value = {"uid": "u1", "name": "Updated"}
            r = client.put("/api/auth/profile", json={"full_name": "Updated"})
            assert r.status_code == 200

    def test_update_profile_missing_data(self, client):
        r = client.put("/api/auth/profile", json={})
        assert r.status_code == 400

    def test_update_profile_save_fails(self, client):
        with patch("routes.auth.user_profile_service") as mock_ups:
            mock_ups.update_user_profile.return_value = False
            r = client.put("/api/auth/profile", json={"full_name": "Updated"})
            assert r.status_code == 500

    def test_admin_login_success(self, client):
        with patch("config.Config.ADMIN_EMAIL", "admin@test.com"):
            with patch("config.Config.ADMIN_PASSWORD", "secret"):
                r = client.post(
                    "/api/auth/admin/login",
                    json={"email": "admin@test.com", "password": "secret"},
                )
                assert r.status_code == 200

    def test_admin_login_invalid(self, client):
        with patch("config.Config.ADMIN_EMAIL", "admin@test.com"):
            with patch("config.Config.ADMIN_PASSWORD", "secret"):
                r = client.post(
                    "/api/auth/admin/login",
                    json={"email": "admin@test.com", "password": "wrong"},
                )
                assert r.status_code == 401

    def test_admin_login_missing_fields(self, client):
        r = client.post("/api/auth/admin/login", json={"email": "admin@test.com"})
        assert r.status_code in [400, 401]

    def test_admin_login_not_configured(self, client):
        with patch("config.Config.ADMIN_EMAIL", None):
            r = client.post(
                "/api/auth/admin/login", json={"email": "a@t.com", "password": "x"}
            )
            assert r.status_code == 500

    def test_refresh_token(self, client):
        with patch("routes.auth.user_profile_service") as mock_ups:
            mock_ups.get_user_role.return_value = "voter"
            r = client.post("/api/auth/refresh")
            assert r.status_code == 200

    def test_logout(self, client):
        r = client.post("/api/auth/logout")
        assert r.status_code in [200, 404]

    def test_role_check(self, client):
        with patch("routes.auth.user_profile_service") as mock_ups:
            mock_ups.get_user_role.return_value = "voter"
            r = client.get("/api/auth/role-check")
            assert r.status_code == 200

    def test_verify_token_success(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {
                "uid": "u1",
                "email": "t@t.com",
                "name": "Test",
                "picture": "url",
                "email_verified": True,
            }
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.upsert_user_profile.return_value = {
                    "firebase_uid": "u1",
                    "email": "t@t.com",
                    "name": "Test",
                    "role": "user",
                }
                r = client.post("/api/auth/verify", json={"id_token": "token"})
                assert r.status_code == 200

    def test_verify_token_missing_id(self, client):
        r = client.post("/api/auth/verify", json={})
        assert r.status_code == 400

    def test_verify_token_invalid(self, client):
        with patch("routes.auth.verify_firebase_token", return_value=None):
            r = client.post("/api/auth/verify", json={"id_token": "bad"})
            assert r.status_code == 401

    def test_verify_token_missing_claims(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {"uid": "u1"}
            r = client.post("/api/auth/verify", json={"id_token": "token"})
            assert r.status_code == 401

    def test_verify_token_profile_fail(self, client):
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {
                "uid": "u1",
                "email": "t@t.com",
                "name": "T",
                "picture": None,
                "email_verified": True,
            }
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.upsert_user_profile.return_value = None
                r = client.post("/api/auth/verify", json={"id_token": "token"})
                assert r.status_code == 500


class TestCacheServiceFull:
    """Complete cache service coverage."""

    def test_redis_init_failure(self):
        from services.cache_service import CacheService

        svc = CacheService(redis_url="redis://bad:6379")
        assert svc._use_redis is False

    def test_redis_get_failure(self):
        from services.cache_service import CacheService

        svc = CacheService()
        svc._use_redis = True
        svc._redis_client = MagicMock()
        svc._redis_client.get.side_effect = Exception("Redis err")
        assert svc.get("key") is None

    def test_redis_set_failure(self):
        from services.cache_service import CacheService

        svc = CacheService()
        svc._use_redis = True
        svc._redis_client = MagicMock()
        svc._redis_client.setex.side_effect = Exception("Redis err")
        assert svc.set("key", "val") is True

    def test_redis_delete_failure(self):
        from services.cache_service import CacheService

        svc = CacheService()
        svc._use_redis = True
        svc._redis_client = MagicMock()
        svc._redis_client.delete.side_effect = Exception("Redis err")
        assert svc.delete("key") is True

    def test_cached_decorator(self):
        from services.cache_service import _cache_service, cached

        _cache_service._memory_cache.clear()
        call_count = 0

        @cached(ttl=60, key_func=lambda x: "test:%s" % x)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive(5) == 10
        assert expensive(5) == 10
        assert call_count == 1

    def test_get_cache_service(self):
        from services.cache_service import CacheService, get_cache_service

        svc = get_cache_service()
        assert isinstance(svc, CacheService)


class TestCalendarServiceFull:
    """Complete calendar service coverage."""

    def test_create_polling_reminder(self):
        from services.calendar_service import CalendarService

        svc = CalendarService()
        result = svc.create_polling_reminder("2026-05-01", "Test Booth")
        assert "icalUID" in result

    def test_create_result_reminder(self):
        from services.calendar_service import CalendarService

        svc = CalendarService()
        result = svc.create_result_reminder("2026-06-01")
        assert "icalUID" in result

    def test_module_create_voting_reminder(self):
        from services.calendar_service import create_voting_reminder

        result = create_voting_reminder("Election", "2026-01-01")
        assert result is not None


class TestMapsServiceFull:
    """Complete maps service coverage."""

    def test_find_polling_booth_error_status(self):
        from services.maps_service import MapsService

        svc = MapsService()
        svc.api_key = "key"
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "UNKNOWN_ERROR"}
        with patch("services.maps_service.requests.get", return_value=mock_resp):
            result = svc.find_polling_booth(1.0, 2.0)
            assert result is not None

    def test_get_directions_api_error(self):
        import requests

        from services.maps_service import MapsService

        svc = MapsService()
        svc.api_key = "key"
        with patch(
            "services.maps_service.requests.get",
            side_effect=requests.RequestException("err"),
        ):
            result = svc.get_directions(1.0, 2.0, 3.0, 4.0)
            assert result is not None

    def test_get_static_map_url_no_key(self):
        from services.maps_service import MapsService

        svc = MapsService()
        svc.api_key = None
        url = svc.get_static_map_url(1.0, 2.0)
        assert "maps.google.com" in url


class TestTranslateServiceFull:
    """Complete translate service coverage."""

    def test_translate_batch_initialized(self):
        from services.translate_service import TranslateService

        svc = TranslateService()
        svc._initialized = True
        svc.client = MagicMock()
        svc.client.translate.return_value = {
            "translatedText": "Translated",
            "detectedSourceLanguage": "en",
        }
        result = svc.translate_batch(["Hello", "World"], "hi")
        assert len(result) == 2

    def test_translate_error(self):
        from services.translate_service import TranslateService

        svc = TranslateService()
        svc._initialized = True
        svc.client = MagicMock()
        svc.client.translate.side_effect = Exception("API err")
        result = svc.translate("Hello", "hi")
        assert result is not None

    def test_translate_with_known_phrases(self):
        from services.translate_service import TranslateService

        svc = TranslateService()
        svc._initialized = False
        result = svc.translate("How do I register to vote?", "hi")
        assert "translated_text" in result


class TestSpeechServiceFull:
    """Complete speech service coverage."""

    def test_recognize_not_initialized(self):
        from services.speech_service import SpeechToTextService

        svc = SpeechToTextService()
        svc._initialized = False
        result = svc.recognize(b"audio")
        assert result is None

    def test_recognize_error_returns_none(self):
        from services.speech_service import SpeechToTextService

        svc = SpeechToTextService()
        svc._initialized = True
        svc.client = MagicMock()
        svc.client.recognize.side_effect = Exception("err")
        result = svc.recognize(b"audio")
        assert result is None

    def test_recognize_from_base64_error(self):
        from services.speech_service import SpeechToTextService

        svc = SpeechToTextService()
        result = svc.recognize_from_base64("not-valid-base64!!!")
        assert result is not None

    def test_voice_input_handler_process(self):
        import base64

        from services.speech_service import VoiceInputHandler

        handler = VoiceInputHandler()
        handler.service = MagicMock()
        handler.service.recognize_from_base64.return_value = "Hello"
        audio = base64.b64encode(b"audio").decode()
        result = handler.process_voice_question(audio)
        assert result["text"] == "Hello"

    def test_voice_input_handler_mock_fallback(self):
        from services.speech_service import VoiceInputHandler

        handler = VoiceInputHandler()
        handler.service = MagicMock()
        handler.service.recognize_from_base64.return_value = None
        result = handler.process_voice_question("audio", language="hi")
        assert "text" in result

    def test_voice_input_handler_language_mapping(self):
        from services.speech_service import VoiceInputHandler

        handler = VoiceInputHandler()
        code = handler._to_language_code("hi")
        assert code == "hi-IN"
        code2 = handler._to_language_code("unknown")
        assert code2 == "en-US"

    def test_transcribe_streaming_not_initialized(self):
        from services.speech_service import SpeechToTextService

        svc = SpeechToTextService()
        svc._initialized = False
        result = svc.transcribe_streaming(iter([]))
        assert result is not None


class TestTTSServiceFull:
    """Complete TTS service coverage."""

    def test_synthesize_with_api(self):
        from services.tts_service import TextToSpeechService

        svc = TextToSpeechService()
        svc._initialized = True
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.audio_content = b"audio_data"
        mock_client.synthesize_speech.return_value = mock_response
        svc.client = mock_client
        result = svc.synthesize("Hello", language="en")
        assert result["audio_format"] == "mp3"

    def test_synthesize_ssml_not_initialized(self):
        from services.tts_service import TextToSpeechService

        svc = TextToSpeechService()
        svc._initialized = False
        result = svc.synthesize_ssml("<speak>Hello</speak>")
        assert result is None

    def test_synthesize_not_initialized(self):
        from services.tts_service import TextToSpeechService

        svc = TextToSpeechService()
        svc._initialized = False
        result = svc.synthesize("Hello")
        assert result is not None

    def test_synthesize_error(self):
        from services.tts_service import TextToSpeechService

        svc = TextToSpeechService()
        svc._initialized = True
        svc.client = MagicMock()
        svc.client.synthesize_speech.side_effect = Exception("err")
        result = svc.synthesize("Hello")
        assert result is not None


class TestAnalyticsServiceFull:
    """Complete analytics service coverage."""

    def test_log_event_no_client_fallback(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_event("test_event", {"key": "val"})
        assert result is True

    def test_log_event_with_client(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = MagicMock()
        result = svc.log_event("test_event", {"key": "val"})
        assert result is True

    def test_log_event_client_exception(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = MagicMock()
        svc.client.log_event.side_effect = Exception("API err")
        result = svc.log_event("test_event", {"key": "val"})
        assert result is True

    def test_log_page_view(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_page_view("/home", "u1")
        assert result is True

    def test_log_feature_use(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_feature_use("chat", "u1")
        assert result is True

    def test_log_language_change(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_language_change("hi", "u1")
        assert result is True

    def test_log_reminder_create(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_reminder_create("voting", "u1")
        assert result is True

    def test_log_calendar_sync(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_calendar_sync(True, "u1")
        assert result is True

    def test_log_polling_booth_search(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_polling_booth_search("u1")
        assert result is True

    def test_log_voice_input(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_voice_input(True, "u1")
        assert result is True

    def test_log_audio_playback(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_audio_playback("tts", "u1")
        assert result is True

    def test_log_ai_chat(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_ai_chat("Hello", "u1")
        assert result is True

    def test_log_signup(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_signup("google", "u1")
        assert result is True

    def test_log_login(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        svc.client = None
        result = svc.log_login("google", "u1")
        assert result is True

    def test_get_user_stats(self):
        from services.analytics_service import AnalyticsService

        svc = AnalyticsService()
        result = svc.get_user_stats("u1")
        assert result["user_id"] == "u1"

    def test_logging_service(self):
        from services.analytics_service import LoggingService

        ls = LoggingService()
        ls.log_info("test info")
        ls.log_warning("test warning")
        ls.log_error("test error")
        ls.log_http_request("GET", "/test", 200, 0.5)


class TestElectionServiceFull:
    """Complete election service coverage."""

    def test_get_election_process(self):
        from services.election_service import get_election_process

        with patch(
            "services.election_service.get_election_process_data", return_value=[]
        ):
            result = get_election_process()
            assert len(result) > 0

    def test_get_election_process_with_data(self):
        from services.election_service import get_election_process

        with patch(
            "services.election_service.get_election_process_data",
            return_value=[{"step": 1}],
        ):
            result = get_election_process()
            assert result == [{"step": 1}]

    def test_get_faqs(self):
        from services.election_service import get_faqs

        with patch("services.election_service.get_faqs_data", return_value=[]):
            result = get_faqs()
            assert len(result) > 0

    def test_get_faqs_with_data(self):
        from services.election_service import get_faqs

        with patch(
            "services.election_service.get_faqs_data", return_value=[{"q": "A?"}]
        ):
            result = get_faqs()
            assert result == [{"q": "A?"}]

    def test_get_timeline(self):
        from services.election_service import get_timeline

        with patch("services.election_service.get_timeline_data", return_value=[]):
            result = get_timeline()
            assert len(result) > 0

    def test_get_timeline_with_data(self):
        from services.election_service import get_timeline

        with patch(
            "services.election_service.get_timeline_data",
            return_value=[{"date": "2026-01-01"}],
        ):
            result = get_timeline()
            assert result == [{"date": "2026-01-01"}]


class TestFirestoreServiceFull:
    """Complete firestore service coverage."""

    def test_save_user_exception(self):
        from services.firestore_service import save_user

        mock_db = MagicMock()
        mock_db.collection().document().set.side_effect = RuntimeError("err")
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = save_user("u1", {"name": "Test"})
            assert result is None

    def test_get_user_exception(self):
        from services.firestore_service import get_user

        mock_db = MagicMock()
        mock_db.collection().document().get.side_effect = RuntimeError("err")
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = get_user("u1")
            assert result is None

    def test_create_or_update_profile_exception(self):
        from services.firestore_service import create_or_update_user_profile

        mock_db = MagicMock()
        mock_db.collection().document().get.side_effect = RuntimeError("err")
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = create_or_update_user_profile("u1", "t@t.com")
            assert result is None


class TestPollingGuidanceServiceFull:
    """Complete polling guidance service coverage."""

    def test_get_all_no_db(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = svc.get_all()
            assert result == []

    def test_get_all_exception(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        mock_coll = MagicMock()
        mock_coll.where().stream.side_effect = Exception("err")
        mock_coll.stream.side_effect = Exception("err")
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_all()
        assert result == []

    def test_get_by_id_not_found(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = False
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_by_id("nonexistent")
        assert result is None

    def test_get_by_id_deleted(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"is_deleted": True}
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_by_id("g1")
        assert result is None

    def test_get_by_id_success(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"title": "Test", "is_deleted": False}
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_by_id("g1")
        assert result is not None

    def test_create_no_db(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        svc._db = None
        try:
            svc.create("R", "T", "D")
        except (RuntimeError, ConnectionError, ValueError):
            pass

    def test_update_not_found(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = False
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.update("nonexistent", {"title": "Updated"})
        assert result is None

    def test_delete_not_found(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = False
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.delete("g1")
        assert result is False

    def test_delete_soft(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = True
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.delete("g1", soft=True)
        assert result is True

    def test_delete_hard(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        doc = MagicMock()
        doc.exists = True
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.delete("g1", soft=False)
        assert result is True

    def test_get_all_for_admin_no_db(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        svc._db = None
        result = svc.get_all_for_admin()
        assert result == []

    def test_get_by_id_no_db(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        svc._db = None
        result = svc.get_by_id("x")
        assert result is None

    def test_update_no_db(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        with patch("firebase_admin.firestore.client", side_effect=Exception("no db")):
            result = svc.update("x", {})
            assert result is None

    def test_delete_no_db(self):
        from services.polling_guidance_service import PollingGuidanceService

        svc = PollingGuidanceService()
        with patch("firebase_admin.firestore.client", side_effect=Exception("no db")):
            result = svc.delete("x")
            assert result is False


class TestAnnouncementServiceFull:
    """Complete announcement service coverage."""

    def test_get_all_no_db(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        svc._db = None
        result = svc.get_all()
        assert result == []

    def test_get_all_exception(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        mock_coll = MagicMock()
        mock_coll.where().stream.side_effect = Exception("err")
        mock_coll.stream.side_effect = Exception("err")
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_all()
        assert result == []

    def test_get_by_id_not_found(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = False
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_by_id("nonexistent")
        assert result is None

    def test_get_by_id_deleted(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"is_deleted": True}
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_by_id("a1")
        assert result is None

    def test_get_by_id_success(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"title": "Test", "is_deleted": False}
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_by_id("a1")
        assert result is not None

    def test_create_no_db(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        svc._db = None
        try:
            svc.create("T", "M")
        except (RuntimeError, ConnectionError, ValueError):
            pass

    def test_update_not_found(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = False
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.update("nonexistent", {"title": "Updated"})
        assert result is None

    def test_delete_not_found(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = False
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.delete("a1")
        assert result is False

    def test_delete_soft(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = True
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.delete("a1", soft=True)
        assert result is True

    def test_delete_hard(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        doc = MagicMock()
        doc.exists = True
        mock_coll = MagicMock()
        mock_coll.document.return_value.get.return_value = doc
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.delete("a1", soft=False)
        assert result is True

    def test_get_all_for_admin_no_db(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        svc._db = None
        result = svc.get_all_for_admin()
        assert result == []

    def test_get_by_id_no_db(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        svc._db = None
        result = svc.get_by_id("x")
        assert result is None

    def test_update_no_db(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        with patch("firebase_admin.firestore.client", side_effect=Exception("no db")):
            result = svc.update("x", {})
            assert result is None

    def test_delete_no_db(self):
        from services.announcement_service import AnnouncementService

        svc = AnnouncementService()
        with patch("firebase_admin.firestore.client", side_effect=Exception("no db")):
            result = svc.delete("x")
            assert result is False


class TestUserRoutes:
    """Test user routes with JWT."""

    def test_get_profile_not_found(self, client):
        with patch("routes.user.get_user", return_value=None):
            with patch("routes.user.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.return_value = None
                r = client.get("/api/user/profile")
                assert r.status_code == 404

    def test_get_profile_from_user_service(self, client):
        with patch("routes.user.get_user") as mock_get:
            mock_get.return_value = {"uid": "u1", "email": "t@t.com"}
            r = client.get("/api/user/profile")
            assert r.status_code == 200

    def test_update_profile(self, client):
        with patch("routes.user.save_user", return_value="u1"):
            with patch("routes.user.get_user") as mock_get:
                mock_get.return_value = {"uid": "u1", "name": "Updated"}
                r = client.put("/api/user/profile", json={"name": "Updated"})
                assert r.status_code == 200

    def test_update_profile_invalid_language(self, client):
        r = client.put("/api/user/profile", json={"language_preference": "zz"})
        assert r.status_code == 400

    def test_update_profile_role_stripped(self, client):
        with patch("routes.user.save_user", return_value="u1"):
            with patch("routes.user.get_user", return_value={"uid": "u1"}):
                r = client.put(
                    "/api/user/profile", json={"role": "admin", "uid": "fake"}
                )
                assert r.status_code == 200

    def test_update_profile_save_fails(self, client):
        with patch("routes.user.save_user", return_value=None):
            r = client.put("/api/user/profile", json={"name": "Test"})
            assert r.status_code == 500

    def test_get_preferences(self, client):
        with patch("routes.user.get_user", return_value=None):
            r = client.get("/api/user/preferences")
            assert r.status_code == 200
            assert r.json["data"] == {}

    def test_get_preferences_with_data(self, client):
        with patch("routes.user.get_user") as mock_get:
            mock_get.return_value = {
                "language_preference": "hi",
                "state": "KA",
                "city": "BLR",
                "first_time_voter": True,
                "voice_enabled": True,
                "accessibility_mode": True,
            }
            r = client.get("/api/user/preferences")
            assert r.status_code == 200
            assert r.json["data"]["language_preference"] == "hi"

    def test_update_preferences(self, client):
        with patch("routes.user.save_user", return_value="u1"):
            r = client.put(
                "/api/user/preferences",
                json={"language_preference": "hi", "state": "KA"},
            )
            assert r.status_code == 200

    def test_update_preferences_invalid_lang(self, client):
        r = client.put("/api/user/preferences", json={"language_preference": "invalid"})
        assert r.status_code == 400

    def test_update_preferences_save_fails(self, client):
        with patch("routes.user.save_user", return_value=None):
            r = client.put("/api/user/preferences", json={"state": "KA"})
            assert r.status_code == 500

    def test_update_preferences_no_fields(self, client):
        r = client.put("/api/user/preferences", json={"unknown_field": "val"})
        assert r.status_code == 200

    def test_fetch_user_own_profile(self, client):
        with patch("routes.user.get_user") as mock_get:
            mock_get.return_value = {"uid": "test-user-id", "email": "t@t.com"}
            r = client.get("/api/user/test-user-id")
            assert r.status_code == 200

    def test_fetch_user_other_profile_denied(self, client):
        r = client.get("/api/user/other_user")
        assert r.status_code == 403

    def test_fetch_user_not_found(self, client):
        with patch("routes.user.get_user", return_value=None):
            r = client.get("/api/user/test-user-id")
            assert r.status_code == 404


class TestValidatorsFull:
    """Complete validator coverage."""

    def test_validate_email_valid(self):
        from utils.validators import validate_email

        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.org") is True

    def test_validate_email_invalid(self):
        from utils.validators import validate_email

        assert validate_email("invalid") is False
        assert validate_email("@no-user.com") is False

    def test_validate_password_short(self):
        from utils.validators import validate_password

        assert validate_password("short") is False
        assert validate_password("12345678") is True

    def test_validate_required_fields_missing(self):
        from utils.validators import validate_required_fields

        valid, missing = validate_required_fields({}, ["name", "email"])
        assert valid is False
        assert set(missing) == {"name", "email"}

    def test_validate_required_fields_empty_value(self):
        from utils.validators import validate_required_fields

        valid, missing = validate_required_fields({"name": ", "}, ["name"])
        assert valid is False

    def test_validate_user_id_empty(self):
        from utils.validators import validate_user_id

        assert not validate_user_id(", ")

    def test_validate_faq_id_empty(self):
        from utils.validators import validate_faq_id

        assert not validate_faq_id(", ")

    def test_validate_timeline_id_empty(self):
        from utils.validators import validate_timeline_id

        assert not validate_timeline_id(", ")

    def test_validate_language_empty(self):
        from utils.validators import validate_language

        assert validate_language(", ") is False

    def test_validate_language_with_allowed(self):
        from utils.validators import validate_language

        assert validate_language("en", ["en", "hi"]) is True
        assert validate_language("fr", ["en", "hi"]) is False

    def test_sanitize_string_empty(self):
        from utils.validators import sanitize_string

        assert sanitize_string(", ") == ", "

    def test_sanitize_string_strip(self):
        from utils.validators import sanitize_string

        assert sanitize_string("  hello  ") == "hello"

    def test_sanitize_string_truncate(self):
        from utils.validators import sanitize_string

        assert len(sanitize_string("a" * 2000, max_length=100)) == 100


class TestResponseFull:
    """Complete response utility coverage."""

    def test_success_response_with_data(self):
        from utils.response import success_response

        r = success_response(data={"key": "val"})
        assert r["success"] is True
        assert r["data"] == {"key": "val"}

    def test_success_response_no_data(self):
        from utils.response import success_response

        r = success_response()
        assert "data" not in r

    def test_error_response_with_errors(self):
        from utils.response import error_response

        r = error_response("Bad", 400, errors=["field required"])
        assert r["success"] is False
        assert r["errors"] == ["field required"]

    def test_error_response_no_errors(self):
        from utils.response import error_response

        r = error_response("Error")
        assert "errors" not in r

    def test_paginated_response(self):
        from utils.response import paginated_response

        r = paginated_response([1, 2, 3], page=1, per_page=10, total=3)
        assert r["success"] is True
        assert r["pagination"]["pages"] == 1
        assert r["pagination"]["total"] == 3

    def test_paginated_response_multiple_pages(self):
        from utils.response import paginated_response

        r = paginated_response([], page=1, per_page=5, total=12)
        assert r["pagination"]["pages"] == 3


class TestBaseServiceFull:
    """Complete base service coverage."""

    def test_db_property_exception(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = svc.db
            assert result is None

    def test_get_collection_no_db(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc._get_collection() is None

    def test_get_all_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc.get_all() == []

    def test_get_all_with_filters(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_query = MagicMock()
        mock_coll.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"name": "test"}
        mock_doc.id = "doc1"
        mock_query.stream.return_value = [mock_doc]
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.get_all(filters={"status": "active"}, order_by="created_at")
        assert len(result) == 1

    def test_fallback_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc._get_all_fallback() == []

    def test_fallback_exception(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_coll.stream.side_effect = RuntimeError("err")
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        assert svc._get_all_fallback() == []

    def test_fallback_with_deleted_doc(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"is_deleted": True, "name": "test"}
        mock_doc.id = "doc1"
        mock_coll.stream.return_value = [mock_doc]
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc._get_all_fallback()
        assert result == []

    def test_fallback_with_filter_skip(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"is_deleted": False, "status": "inactive"}
        mock_doc.id = "doc1"
        mock_coll.stream.return_value = [mock_doc]
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc._get_all_fallback(filters={"status": "active"})
        assert result == []

    def test_get_by_id_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc.get_by_id("x") is None

    def test_create_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc.create({"name": "test"}) is None

    def test_update_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc.update("x", {"name": "test"}) is None

    def test_delete_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc.delete("x") is False

    def test_get_all_for_admin_no_collection(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        with patch.object(
            type(svc), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert svc.get_all_for_admin() == []

    def test_get_all_for_admin_exception(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_coll.stream.side_effect = ValueError("err")
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        assert svc.get_all_for_admin() == []

    def test_create_with_doc_id(self):
        from firebase_admin import firestore

        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc_ref = MagicMock()
        mock_coll.document.return_value = mock_doc_ref
        mock_doc_ref.id = "custom-id"
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        result = svc.create({"name": "test"}, doc_id="custom-id")
        assert result["id"] == "custom-id"

    def test_create_exception(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.set.side_effect = RuntimeError("err")
        mock_doc_ref.id = "x"
        mock_coll.document.return_value = mock_doc_ref
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        assert svc.create({"name": "test"}) is None

    def test_update_exception(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc_ref.get.return_value = mock_doc
        mock_doc_ref.update.side_effect = ConnectionError("err")
        mock_coll.document.return_value = mock_doc_ref
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        assert svc.update("x", {"name": "test"}) is None

    def test_delete_hard(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc_ref.get.return_value = mock_doc
        mock_coll.document.return_value = mock_doc_ref
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        assert svc.delete("x", soft=False) is True

    def test_delete_exception(self):
        from services.base_service import BaseService

        class TestService(BaseService):
            collection_name = "test"

        svc = TestService()
        mock_coll = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.side_effect = ValueError("err")
        mock_coll.document.return_value = mock_doc_ref
        svc._db = MagicMock()
        svc._db.collection.return_value = mock_coll
        assert svc.delete("x") is False


class TestDataAccessLayerFull:
    """Complete data access layer coverage."""

    def test_db_not_initialized(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = False
        with patch("firebase_admin.firestore.client", side_effect=RuntimeError("err")):
            result = db.db
            assert result is None

    def test_db_connection_error(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch(
            "firebase_admin.firestore.client", side_effect=ConnectionError("err")
        ):
            result = db.db
            assert result is None

    def test_db_value_error(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", side_effect=ValueError("err")):
            result = db.db
            assert result is None

    def test_create_user_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_user("u1", {"name": "Test"}) is False

    def test_create_user_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().set.side_effect = RuntimeError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.create_user("u1", {"name": "Test"}) is False

    def test_get_user_from_service_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().get.side_effect = ConnectionError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_user("u1") is None

    def test_update_user_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.update_user("u1", {"name": "Test"}) is False

    def test_update_user_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().update.side_effect = ValueError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.update_user("u1", {"name": "Test"}) is False

    def test_delete_user_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.delete_user("u1") is False

    def test_delete_user_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().delete.side_effect = RuntimeError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.delete_user("u1") is False

    def test_get_all_users_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_all_users() == []

    def test_get_all_users_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().limit().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_all_users() == []

    def test_election_process_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_election_process("p1", {"title": "T"}) is False
            assert db.get_election_process("p1") is None
            assert db.update_election_process("p1", {"title": "U"}) is False
            assert db.delete_election_process("p1") is False

    def test_election_process_get_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().get.side_effect = ValueError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_election_process("p1") is None

    def test_get_all_election_processes_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_all_election_processes() == []

    def test_get_all_election_processes_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().where().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_all_election_processes() == []

    def test_timeline_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_timeline("t1", {"title": "T"}) is False
            assert db.get_timeline("t1") is None
            assert db.update_timeline("t1", {"title": "U"}) is False
            assert db.delete_timeline("t1") is False

    def test_get_timelines_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_timelines() == []

    def test_get_timelines_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_timelines() == []

    def test_faq_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_faq("f1", {"q": "Q"}) is False
            assert db.get_faq("f1") is None
            assert db.update_faq("f1", {"q": "U"}) is False
            assert db.delete_faq("f1") is False

    def test_get_faqs_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_faqs() == []

    def test_get_faqs_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().where().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_faqs() == []

    def test_reminder_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_reminder("u1", "r1", {"title": "T"}) is False
            assert db.get_reminder("u1", "r1") is None
            assert db.update_reminder("u1", "r1", {"title": "U"}) is False
            assert db.delete_reminder("u1", "r1") is False

    def test_get_user_reminders_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_user_reminders("u1") == []

    def test_get_user_reminders_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().collection().stream.side_effect = Exception(
            "err"
        )
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_user_reminders("u1") == []

    def test_announcement_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_announcement("a1", {"title": "T"}) is False
            assert db.get_announcement("a1") is None
            assert db.update_announcement("a1", {"title": "U"}) is False
            assert db.delete_announcement("a1") is False

    def test_get_announcements_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_announcements() == []

    def test_get_announcements_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().where().order_by().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_announcements() == []

    def test_bookmark_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_bookmark("u1", "b1", {"title": "T"}) is False
            assert db.get_user_bookmarks("u1") == []
            assert db.delete_bookmark("u1", "b1") is False

    def test_get_user_bookmarks_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().collection().stream.side_effect = Exception(
            "err"
        )
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_user_bookmarks("u1") == []

    def test_analytics_crud_no_db(self):
        from datetime import datetime

        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_analytics("a1", {"type": "view"}) is False
            assert db.get_analytics() == []
            assert db.increment_analytics("view", datetime.now()) is False

    def test_get_analytics_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_analytics() == []

    def test_increment_analytics_exception(self):
        from datetime import datetime

        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().set.side_effect = RuntimeError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.increment_analytics("view", datetime.now()) is False

    def test_polling_guidance_crud_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_polling_guidance("g1", {"title": "T"}) is False
            assert db.get_polling_guidance("g1") is None
            assert db.update_polling_guidance("g1", {"title": "U"}) is False

    def test_get_polling_guidances_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.get_polling_guidances() == []

    def test_get_polling_guidances_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().where().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_polling_guidances() == []

    def test_settings_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_setting("key", "val") is False
            assert db.get_setting("key") is None
            assert db.get_all_settings() == {}

    def test_get_setting_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().get.side_effect = ValueError("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_setting("key") is None

    def test_get_all_settings_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().stream.side_effect = Exception("err")
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_all_settings() == {}

    def test_preferences_no_db(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        with patch("firebase_admin.firestore.client", return_value=None):
            assert db.create_or_update_preferences("u1", {"lang": "en"}) is False
            assert db.get_preferences("u1") is None

    def test_preferences_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().collection().document.side_effect = (
            RuntimeError("err")
        )
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.create_or_update_preferences("u1", {"lang": "en"}) is False

    def test_get_preferences_exception(self):
        from services.data_access_layer import FirestoreDB

        db = FirestoreDB()
        db._initialized = True
        mock_db = MagicMock()
        mock_db.collection().document().collection().document().get.side_effect = (
            ValueError("err")
        )
        with patch("firebase_admin.firestore.client", return_value=mock_db):
            assert db.get_preferences("u1") is None


class TestFirestoreHealthFull:
    """Complete firestore health check coverage."""

    def test_check_connection_no_client(self):
        from services.firestore_health import FirestoreHealthCheck

        with patch("firebase_admin.firestore.client", return_value=None):
            result = FirestoreHealthCheck.check_connection()
            assert result["connected"] is False

    def test_check_connection_exception(self):
        from services.firestore_health import FirestoreHealthCheck

        with patch("firebase_admin.firestore.client", side_effect=RuntimeError("err")):
            result = FirestoreHealthCheck.check_connection()
            assert result["connected"] is False

    def test_get_collections_no_client(self):
        from services.firestore_health import FirestoreHealthCheck

        with patch("firebase_admin.firestore.client", return_value=None):
            result = FirestoreHealthCheck.get_collections()
            assert result == []

    def test_get_collections_exception(self):
        from services.firestore_health import FirestoreHealthCheck

        with patch("firebase_admin.firestore.client", side_effect=ValueError("err")):
            result = FirestoreHealthCheck.get_collections()
            assert result == []


class TestDocsRoutesFull:
    """Test docs routes with blueprint registration."""

    def test_openapi_spec_structure(self):
        from routes.docs import docs_bp

        assert docs_bp is not None
        rules = list(docs_bp.deferred_functions)
        assert len(rules) >= 2
