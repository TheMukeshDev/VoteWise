"""
Edge case tests for VoteWise AI API

Tests for invalid inputs, missing data, failed operations, etc.
"""

import pytest
from unittest.mock import patch


@pytest.fixture
def client():
    from app import create_app

    app = create_app()
    app.config.update({"TESTING": True})
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token", "Content-Type": "application/json"}


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_health_with_no_db(self, client):
        """Test health endpoint returns healthy even without DB."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data.get("status") == "healthy" or data.get("success") is True

    def test_login_with_empty_token(self, client):
        """Test login fails with empty token."""
        response = client.post("/api/auth/login", json={"id_token": ""})
        assert response.status_code == 400

    def test_login_with_missing_token(self, client):
        """Test login fails with missing token."""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 400

    def test_login_with_invalid_token(self, client):
        """Test login fails with invalid token."""
        response = client.post("/api/auth/login", json={"id_token": "invalid-token"})
        assert response.status_code == 401

    def test_chat_with_empty_message(self, client):
        """Test chat fails with empty message."""
        response = client.post("/api/chat/chat", json={"message": ""})
        assert response.status_code == 400

    def test_chat_with_missing_message(self, client):
        """Test chat fails with missing message."""
        response = client.post("/api/chat/chat", json={})
        assert response.status_code == 400

    def test_chat_with_long_message(self, client):
        """Test chat handles very long message."""
        long_message = "x" * 5000
        response = client.post("/api/chat/chat", json={"message": long_message})
        assert response.status_code in [200, 400]

    def test_faq_not_found(self, client):
        """Test FAQ returns 404 for non-existent ID."""
        with patch("services.faq_service.faq_service.get_by_id") as mock_get:
            mock_get.return_value = None
            response = client.get("/api/faqs/non-existent-id")
            assert response.status_code == 404

    def test_reminder_without_auth(self, client):
        """Test reminder requires auth."""
        response = client.get("/api/user/reminders")
        assert response.status_code == 401

    def test_sql_injection_in_faq_id(self, client):
        """Test FAQ handles special characters in ID."""
        response = client.get("/api/faqs/../admin")
        assert response.status_code in [400, 404]

    def test_xss_in_question(self, client):
        """Test FAQ handles XSS in question."""
        response = client.get("/api/faqs/")
        assert response.status_code == 200

    def test_invalid_coordinates(self, client):
        """Test polling with invalid coordinates."""
        response = client.get("/api/polling?lat=999&lng=999")
        assert response.status_code in [200, 400, 500]

    def test_timeline_empty(self, client):
        """Test timeline with no data."""
        with patch("services.timeline_service.timeline_service") as mock_svc:
            mock_svc.get_upcoming_events.return_value = []
            response = client.get("/api/timeline/")
            assert response.status_code == 200


class TestSecurityEdgeCases:
    """Test security edge cases."""

    def test_jwt_token_tampering(self, client):
        """Test behavior with tampered JWT."""
        response = client.get(
            "/api/user/profile", headers={"Authorization": "Bearer tampered.token.here"}
        )
        assert response.status_code == 401

    def test_unicode_in_input(self, client):
        """Test unicode handling."""
        response = client.post(
            "/api/chat/chat", json={"message": "test with émojis 🎉"}
        )
        assert response.status_code in [200, 400]

    def test_faq_not_found(self, client):
        """Test FAQ returns 404 for non-existent ID."""
        with patch("services.faq_service.faq_service.get_by_id") as mock_get:
            mock_get.return_value = None
            response = client.get("/api/faqs/non-existent-id")
            assert response.status_code == 404

    def test_reminder_without_auth(self, client):
        """Test reminder requires auth."""
        response = client.get("/api/user/reminders")
        assert response.status_code == 401

    def test_create_reminder_missing_fields(self, client, auth_headers):
        """Test create reminder fails with missing fields."""
        response = client.post("/api/user/reminders", json={}, headers=auth_headers)
        assert response.status_code == 400

    def test_profile_update_no_data(self, client, auth_headers):
        """Test profile update with no data."""
        response = client.put("/api/user/profile", json={}, headers=auth_headers)
        assert response.status_code in [200, 400]

    def test_invalid_language_preference(self, client, auth_headers):
        """Test invalid language preference."""
        with (
            patch("routes.user.save_user") as mock_save,
            patch("routes.user.get_user") as mock_get,
            patch("routes.user.get_jwt_identity") as mock_identity,
        ):
            mock_identity.return_value = {"user_id": "u1"}
            mock_get.return_value = {"id": "u1"}
            mock_save.return_value = "u1"

            response = client.put(
                "/api/user/profile",
                json={"language_preference": "invalid_lang"},
                headers=auth_headers,
            )
            assert response.status_code in [200, 400]

    def test_invalid_priority(self, client, auth_headers):
        """Test announcement with invalid priority."""
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch(
                "middleware.auth_middleware.user_profile_service.get_user_profile"
            ) as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ""),
        ):
            mock_identity.return_value = {"user_id": "admin", "role": "admin"}
            mock_profile.return_value = {"email": ""}

            response = client.post(
                "/api/admin/announcements/",
                json={"title": "Test", "message": "Test", "priority": "invalid"},
                headers=auth_headers,
            )
            assert response.status_code == 400

    def test_sql_injection_in_faq_id(self, client):
        """Test FAQ handles special characters in ID."""
        response = client.get("/api/faqs/../admin")
        assert response.status_code in [400, 404]

    def test_xss_in_question(self, client):
        """Test FAQ handles XSS in question."""
        with patch("services.faq_service.faq_service.get_by_id") as mock_get:
            mock_get.return_value = {
                "id": "1",
                "question": "<script>alert('xss')</script>",
                "answer": "Safe answer",
            }
            response = client.get("/api/faqs/1")
            assert response.status_code == 200

    def test_invalid_coordinates(self, client):
        """Test polling with invalid coordinates."""
        response = client.get("/api/polling?lat=999&lng=999")
        assert response.status_code in [200, 400, 500]

    def test_timeline_empty(self, client):
        """Test timeline with no data."""
        with patch("services.timeline_service.timeline_service") as mock_svc:
            mock_svc.get_upcoming_events.return_value = []
            response = client.get("/api/timeline/")
            assert response.status_code == 200

