"""
Tests for authentication routes.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestAuthRoutes:
    """Test authentication endpoints."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "service" in data

    def test_login_missing_token(self, client):
        """Test login with missing token returns error."""
        response = client.post(
            "/api/auth/login", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_login_invalid_token(self, client):
        """Test login with invalid token returns error."""
        with patch(
            "middleware.auth_middleware.verify_firebase_token", return_value=None
        ):
            response = client.post(
                "/api/auth/login",
                data=json.dumps({"id_token": "invalid-token"}),
                content_type="application/json",
            )
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data["success"] is False

    def test_login_success(self, client, mock_firebase_auth, mock_firestore):
        """Test successful login flow."""
        with (
            patch("middleware.auth_middleware.verify_firebase_token") as mock_verify,
            patch(
                "services.auth_service.user_profile_service.get_user_profile"
            ) as mock_get,
        ):
            mock_verify.return_value = {
                "uid": "test-user-id",
                "email": "test@example.com",
                "name": "Test User",
            }
            mock_get.return_value = {
                "user_id": "test-user-id",
                "email": "test@example.com",
                "role": "voter",
            }

            response = client.post(
                "/api/auth/login",
                data=json.dumps({"id_token": "valid-test-token"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "access_token" in data["data"]

    def test_register_missing_token(self, client):
        """Test registration with missing token."""
        response = client.post(
            "/api/auth/register", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400

    def test_register_invalid_token(self, client):
        """Test registration with invalid token."""
        with patch(
            "middleware.auth_middleware.verify_firebase_token", return_value=None
        ):
            response = client.post(
                "/api/auth/register",
                data=json.dumps({"id_token": "invalid-token"}),
                content_type="application/json",
            )
            assert response.status_code == 401

    def test_get_current_user_no_auth(self, client):
        """Test accessing protected route without auth."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_google_signin_missing_token(self, client):
        """Test Google sign-in with missing token."""
        response = client.post(
            "/api/auth/google-signin",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_google_signin_invalid_token(self, client):
        """Test Google sign-in with invalid token."""
        with patch(
            "middleware.auth_middleware.verify_firebase_token", return_value=None
        ):
            response = client.post(
                "/api/auth/google-signin",
                data=json.dumps({"id_token": "invalid-token"}),
                content_type="application/json",
            )
            assert response.status_code == 401


class TestAuthSecurity:
    """Test authentication security."""

    def test_no_token_in_response_data(self, client):
        """Ensure sensitive data is not leaked in responses."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"id_token": "test-token"}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        response_str = json.dumps(data)
        assert "password" not in response_str.lower()

    def test_error_messages_safe(self, client):
        """Ensure error messages don't leak sensitive info."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"id_token": "malicious-token"}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        response_text = json.dumps(data).lower()
        assert "credential" not in response_text
        assert "api_key" not in response_text
