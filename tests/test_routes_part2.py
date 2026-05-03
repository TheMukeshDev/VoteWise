import pytest
from unittest.mock import patch
import json


@pytest.fixture(autouse=True)
def mock_jwt():
    ", ", "Mock JWT for all protected routes.", ", "
    with (
        patch(
            "flask_jwt_extended.view_decorators.verify_jwt_in_request"
        ) as mock_verify,
        patch("middleware.auth_middleware.verify_jwt_in_request") as mock_mw_verify,
        patch("middleware.auth_middleware.get_jwt_identity") as mock_mw_identity,
        patch("middleware.auth_middleware.user_profile_service") as mock_profile,
    ):
        mock_verify.return_value = None
        mock_mw_verify.return_value = None
        mock_mw_identity.return_value = {"user_id": "u1", "role": "admin"}
        mock_profile.get_user_profile.return_value = {
            "id": "u1",
            "email": "admin@example.com",
            "role": "admin",
        }
        mock_profile.get_user_role.return_value = "admin"
        yield


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer test-access-token",
        "Content-Type": "application/json",
    }


class TestBookmarkRoutes:
    @patch("routes.bookmark.get_bookmarks")
    @patch("routes.bookmark.get_jwt_identity")
    def test_get_bookmarks(
        self, mock_identity, mock_get_bookmarks, client, auth_headers
    ):
        mock_identity.return_value = {"user_id": "u1"}
        mock_get_bookmarks.return_value = []
        res = client.get("/api/user/bookmarks/", headers=auth_headers)
        assert res.status_code == 200

    @patch("routes.bookmark.get_bookmark_by_resource")
    @patch("routes.bookmark.save_bookmark")
    @patch("routes.bookmark.get_jwt_identity")
    def test_add_bookmark(
        self, mock_identity, mock_save_bookmark, mock_get_bookmark, client, auth_headers
    ):
        mock_identity.return_value = {"user_id": "u1"}
        mock_get_bookmark.return_value = None
        mock_save_bookmark.return_value = "b1"
        res = client.post(
            "/api/user/bookmarks/",
            data=json.dumps({"resource_id": "i1", "resource_type": "faq"}),
            headers=auth_headers,
        )
        assert res.status_code == 201


class TestAnnouncementAdminRoutes:
    def test_get_announcements(self, client, auth_headers):
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch("services.announcement_service.announcement_service") as mock_svc,
            patch(
                "middleware.auth_middleware.user_profile_service.get_user_profile"
            ) as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ", "),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ", "}
            mock_svc.get_all_for_admin.return_value = []
            res = client.get("/api/admin/announcements/", headers=auth_headers)
            assert res.status_code == 200

    def test_create_announcement(self, client, auth_headers):
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch(
                "services.announcement_service.AnnouncementService.create"
            ) as mock_create,
            patch(
                "middleware.auth_middleware.user_profile_service.get_user_profile"
            ) as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ", "),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ", "}
            mock_create.return_value = {"id": "a1", "title": "A1", "message": "C1"}
            res = client.post(
                "/api/admin/announcements/",
                data=json.dumps({"title": "A1", "message": "C1"}),
                headers=auth_headers,
            )
            assert res.status_code == 201


class TestElectionProcessAdminRoutes:
    def test_get_processes(self, client, auth_headers):
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch(
                "services.election_process_service.election_process_service"
            ) as mock_ep_svc,
            patch(
                "middleware.auth_middleware.user_profile_service.get_user_profile"
            ) as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ", "),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ", "}
            mock_ep_svc.get_all.return_value = []
            res = client.get("/api/admin/election-process/", headers=auth_headers)
            assert res.status_code == 200


class TestPollingGuidanceAdminRoutes:
    def test_get_guidance(self, client, auth_headers):
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch(
                "services.polling_guidance_service.polling_guidance_service"
            ) as mock_pg_svc,
            patch(
                "middleware.auth_middleware.user_profile_service.get_user_profile"
            ) as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ", "),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ", "}
            mock_pg_svc.get_all.return_value = []
            res = client.get("/api/admin/polling-guidance/", headers=auth_headers)
            assert res.status_code == 200


class TestTimelinePublicRoutes:
    @patch("services.timeline_service.timeline_service")
    def test_get_public_timeline(self, mock_timeline_svc, client):
        mock_timeline_svc.get_upcoming_events.return_value = []
        res = client.get("/api/timeline/")
        assert res.status_code == 200


class TestTimelineAdminRoutes:
    def test_get_admin_timeline(self, client, auth_headers):
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch("services.timeline_service.timeline_service") as mock_timeline_svc,
            patch(
                "middleware.auth_middleware.user_profile_service.get_user_profile"
            ) as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ", "),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ", "}
            mock_timeline_svc.get_all_events.return_value = []
            res = client.get("/api/admin/timelines/", headers=auth_headers)
            assert res.status_code == 200


class TestSpeechRoutes:
    @patch("routes.speech.stt_service")
    def test_process_speech(self, mock_stt, client):
        mock_stt.recognize.return_value = "Hello"
        res = client.post(
            "/api/speech/speech-to-text",
            data=json.dumps({"audio_data": "base64"}),
            headers={"Content-Type": "application/json"},
        )
        assert res.status_code == 200

    @patch("routes.speech.tts_service")
    def test_synthesize_speech(self, mock_tts, client):
        mock_tts.text_to_speech.return_value = {"audioContent": "base64"}
        res = client.post(
            "/api/speech/text-to-speech",
            data=json.dumps({"text": "Hello"}),
            headers={"Content-Type": "application/json"},
        )
        assert res.status_code == 200


class TestUserProfileRoutes:
    @patch("routes.user.get_user")
    @patch("routes.user.get_jwt_identity")
    def test_get_profile(self, mock_identity, mock_get_user, client, auth_headers):
        mock_identity.return_value = {"user_id": "u1"}
        mock_get_user.return_value = {"id": "u1", "name": "User"}
        res = client.get("/api/user/profile", headers=auth_headers)
        assert res.status_code == 200

    @patch("routes.user.get_user")
    @patch("routes.user.save_user")
    @patch("routes.user.get_jwt_identity")
    def test_update_profile(
        self, mock_identity, mock_save_user, mock_get_user, client, auth_headers
    ):
        mock_identity.return_value = {"user_id": "u1"}
        mock_save_user.return_value = "u1"
        mock_get_user.return_value = {"id": "u1"}
        res = client.put(
            "/api/user/profile",
            data=json.dumps({"language_preference": "hi"}),
            headers=auth_headers,
        )
        assert res.status_code == 200

    @patch("routes.user.get_user")
    @patch("routes.user.get_jwt_identity")
    def test_get_preferences(self, mock_identity, mock_get_user, client, auth_headers):
        mock_identity.return_value = {"user_id": "u1"}
        mock_get_user.return_value = {"id": "u1", "language_preference": "hi"}
        res = client.get("/api/user/preferences", headers=auth_headers)
        assert res.status_code == 200
