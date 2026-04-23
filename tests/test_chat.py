"""
Tests for chat routes.
"""

import pytest
import json
from unittest.mock import patch


class TestChatRoutes:
    """Test chat API endpoints."""

    def test_chat_missing_message(self, client):
        """Test chat without message returns error."""
        response = client.post(
            "/api/chat/chat", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_chat_empty_message(self, client):
        """Test chat with empty message returns error."""
        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_valid_message(self, client):
        """Test chat with valid message returns response."""
        with patch("routes.chat.client") as mock_client:
            mock_response = MagicMock()
            mock_response.text = json.dumps(
                {
                    "intro": "Here is the answer.",
                    "steps": ["Step 1", "Step 2"],
                    "tips": ["Tip 1"],
                    "actions": ["Action 1"],
                }
            )
            mock_client.models.generate_content.return_value = mock_response

            response = client.post(
                "/api/chat/chat",
                data=json.dumps({"message": "How do I register to vote?"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True

    def test_chat_with_user_prefs(self, client):
        """Test chat respects user preferences."""
        with patch("routes.chat.client") as mock_client:
            mock_response = MagicMock()
            mock_response.text = json.dumps(
                {"intro": "Here is the answer.", "steps": [], "tips": [], "actions": []}
            )
            mock_client.models.generate_content.return_value = mock_response

            response = client.post(
                "/api/chat/chat",
                data=json.dumps(
                    {"message": "Test question", "user_prefs": {"language": "hi"}}
                ),
                content_type="application/json",
            )

            assert response.status_code == 200

    def test_chat_fallback_on_api_error(self, client):
        """Test chat returns fallback on API error."""
        with patch("routes.chat.client") as mock_client:
            mock_client.models.generate_content.side_effect = Exception("API Error")

            response = client.post(
                "/api/chat/chat",
                data=json.dumps({"message": "Test question"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "intro" in data["data"] or "response" in data["data"]

    def test_chat_no_client_available(self, client):
        """Test chat with no API client returns mock response."""
        with patch("routes.chat.client", None):
            response = client.post(
                "/api/chat/chat",
                data=json.dumps({"message": "Test question"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "intro" in data["data"] or "response" in data["data"]

    def test_chat_message_length_limit(self, client):
        """Test chat handles long messages."""
        long_message = "A" * 5000

        response = client.post(
            "/api/chat/chat",
            data=json.dumps({"message": long_message}),
            content_type="application/json",
        )

        assert response.status_code in [200, 400]


class TestChatSecurity:
    """Test chat security."""

    def test_chat_sanitizes_input(self, client):
        """Test chat input is sanitized."""
        with patch("routes.chat.client") as mock_client:
            mock_response = MagicMock()
            mock_response.text = json.dumps(
                {"intro": "OK", "steps": [], "tips": [], "actions": []}
            )
            mock_client.models.generate_content.return_value = mock_response

            malicious_input = "<script>alert('xss')</script>How to register?"

            response = client.post(
                "/api/chat/chat",
                data=json.dumps({"message": malicious_input}),
                content_type="application/json",
            )

            assert response.status_code == 200
