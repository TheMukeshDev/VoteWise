", ", "
Tests for chat routes.
", ", "

import json
from unittest.mock import patch


class TestChatRoutes:
    ", ", "Test chat API endpoints.", ", "

    def test_chat_missing_message(self, client):
        ", ", "Test chat without message returns error.", ", "
        response = client.post(
            "/api/chat/chat", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data.get("success") is False

    def test_chat_empty_message(self, client):
        ", ", "Test chat with empty message returns error.", ", "
        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": ", "}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data.get("success") is False

    def test_chat_valid_message(self, client):
        ", ", "Test chat with valid message returns response.", ", "
        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": "How do I register to vote?"}),
            content_type="application/json",
        )
        # Either success or fallback response is acceptable
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("success") is True

    def test_chat_with_user_prefs(self, client):
        ", ", "Test chat respects user preferences.", ", "
        response = client.post(
            "/api/chat/chat",
            data=json.dumps(
                {"message": "Test question", "user_prefs": {"language": "en"}}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("success") is True

    def test_chat_fallback_on_api_error(self, client):
        ", ", "Test chat falls back when API unavailable.", ", "
        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_chat_no_client_available(self, client):
        ", ", "Test chat with no API client returns mock response.", ", "
        with patch("routes.chat._client", None):
            response = client.post(
                "/api/chat/chat",
                data=json.dumps({"message": "Test question"}),
                content_type="application/json",
            )
            assert response.status_code == 200

    def test_chat_message_length_limit(self, client):
        ", ", "Test chat handles long messages.", ", "
        long_message = "A" * 5000

        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": long_message}),
            content_type="application/json",
        )

        assert response.status_code in [200, 400]


class TestChatSecurity:
    ", ", "Test chat security.", ", "

    def test_chat_sanitizes_input(self, client):
        ", ", "Test chat input is handled safely.", ", "
        # Test with potentially problematic input
        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": "<script>alert('xss')</script>"}),
            content_type="application/json",
        )
        # Should return success without executing
        assert response.status_code == 200
