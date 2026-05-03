"""
Tests for authentication routes.
"""

import json
from unittest.mock import patch


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
        with patch("routes.auth.verify_firebase_token", return_value=None):
            response = client.post(
                "/api/auth/login",
                data=json.dumps({"id_token": "invalid-token"}),
                content_type="application/json",
            )
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data["success"] is False

    def test_login_success(self, client):
        """Test successful login flow."""
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {
                "uid": "test-user-id",
                "email": "test@example.com",
                "name": "Test User",
            }

            response = client.post(
                "/api/auth/login",
                data=json.dumps({"id_token": "valid-test-token"}),
                content_type="application/json",
            )

            # Either success or 500 (if user_profile_service is not mocked) is acceptable
            assert (
                response.status_code == 200
            )  # Fixed: 500 is not a valid success status

    def test_register_missing_token(self, client):
        """Test registration with missing token."""
        response = client.post(
            "/api/auth/register", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400

    def test_register_invalid_token(self, client):
        """Test registration with invalid token."""
        with patch("routes.auth.verify_firebase_token", return_value=None):
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
        with patch("routes.auth.verify_firebase_token", return_value=None):
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


class TestTokenVerification:
    """Test token verification endpoint."""

    def test_verify_token_valid(self, client):
        """Test token verification with valid token."""
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = {
                "uid": "test-user-123",
                "email": "test@example.com",
                "name": "Test User",
            }
            with patch("routes.auth.user_profile_service") as mock_ups:
                mock_ups.get_user_profile.return_value = {
                    "uid": "test-user-123",
                    "email": "test@example.com",
                    "role": "voter",
                }
                mock_ups.create_user_profile.return_value = True
                mock_ups.update_last_login.return_value = True
                response = client.post(
                    "/api/auth/login",
                    data=json.dumps({"id_token": "valid-firebase-token"}),
                    content_type="application/json",
                )
                assert response.status_code == 200

    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token."""
        with patch("routes.auth.verify_firebase_token") as mock_verify:
            mock_verify.return_value = None
            response = client.post(
                "/api/auth/login",
                data=json.dumps({"id_token": "invalid-firebase-token"}),
                content_type="application/json",
            )
            assert response.status_code == 401

    def test_verify_token_missing(self, client):
        """Test token verification with missing token."""
        response = client.post(
            "/api/auth/login",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_admin_login_valid(self, client):
        """Test admin login with valid credentials."""
        with patch("config.Config.ADMIN_EMAIL", "admin@example.com"):
            with patch("config.Config.ADMIN_PASSWORD", "adminpassword"):
                response = client.post(
                    "/api/auth/admin/login",
                    data=json.dumps(
                        {"email": "admin@example.com", "password": "adminpassword"}
                    ),
                    content_type="application/json",
                )
                assert response.status_code == 200

    def test_admin_login_invalid(self, client):
        """Test admin login with invalid credentials."""
        with patch("config.Config.ADMIN_EMAIL", "admin@example.com"):
            with patch("config.Config.ADMIN_PASSWORD", "adminpassword"):
                response = client.post(
                    "/api/auth/admin/login",
                    data=json.dumps(
                        {"email": "admin@example.com", "password": "wrongpassword"}
                    ),
                    content_type="application/json",
                )
                assert response.status_code == 401
