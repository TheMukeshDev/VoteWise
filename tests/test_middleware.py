from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, jsonify

from middleware.auth_middleware import (
    AuthMiddleware,
    check_rate_limit,
    generate_tokens,
    get_current_user,
    get_current_user_role,
    require_admin,
    require_auth,
    require_voter,
    setup_auth_middleware,
    verify_firebase_token,
)


class TestAuthMiddleware:
    def test_check_rate_limit(self):
        key = "test_key"

        # Should allow 2 requests
        assert check_rate_limit(key, max_requests=2, window_seconds=10) is True
        assert check_rate_limit(key, max_requests=2, window_seconds=10) is True

        # 3rd request should fail
        assert check_rate_limit(key, max_requests=2, window_seconds=10) is False

    def test_auth_middleware_class(self):
        middleware = AuthMiddleware()
        middleware.firebase_service = MagicMock()
        middleware.profile_service = MagicMock()

        # Test authenticate_firebase_token
        middleware.firebase_service.verify_id_token.return_value = {"uid": "u1"}
        middleware.profile_service.get_user_profile.return_value = {"id": "u1"}
        assert middleware.authenticate_firebase_token("token") == {"id": "u1"}
        middleware.profile_service.update_last_login.assert_called_with("u1")

        middleware.firebase_service.verify_id_token.return_value = None
        assert middleware.authenticate_firebase_token("token") is None

        # Test get_or_create_user
        middleware.profile_service.get_user_profile.return_value = None
        middleware.profile_service.create_user_profile.return_value = True
        middleware.get_or_create_user({"uid": "u1", "email": "a@b.com"})
        middleware.profile_service.create_user_profile.assert_called()

        # Test check_permission
        middleware.profile_service.get_user_role.return_value = "voter"
        assert middleware.check_permission("u1", "user", "read") is True
        assert middleware.check_permission("u1", "faq", "write") is False

        middleware.profile_service.get_user_role.return_value = "admin"
        assert middleware.check_permission("u1", "faq", "write") is True


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret"
    setup_auth_middleware(app)

    @app.route("/protected")
    @require_auth
    def protected():
        return jsonify({"user": get_current_user(), "role": get_current_user_role()})

    @app.route("/admin")
    @require_admin
    def admin():
        return jsonify({"msg": "admin"})

    @app.route("/voter")
    @require_voter
    def voter():
        return jsonify({"msg": "voter"})

    return app


class TestDecorators:
    @patch("middleware.auth_middleware.verify_jwt_in_request")
    @patch("middleware.auth_middleware.get_jwt_identity")
    @patch("middleware.auth_middleware.user_profile_service")
    def test_require_auth(self, mock_profile_svc, mock_identity, mock_verify, app):
        mock_identity.return_value = {"user_id": "u1", "role": "voter"}
        mock_profile_svc.get_user_profile.return_value = {"id": "u1", "name": "Test"}

        with app.test_client() as client:
            res = client.get("/protected")
            assert res.status_code == 200
            assert res.json["user"]["id"] == "u1"
            assert res.json["role"] == "voter"

        mock_verify.side_effect = Exception("Invalid token")
        with app.test_client() as client:
            res = client.get("/protected")
            assert res.status_code == 401

    @patch("middleware.auth_middleware.verify_jwt_in_request")
    @patch("middleware.auth_middleware.get_jwt_identity")
    @patch("middleware.auth_middleware.user_profile_service")
    def test_require_roles(self, mock_profile_svc, mock_identity, mock_verify, app):
        # Admin passing
        mock_identity.return_value = {"user_id": "u1", "role": "admin"}
        mock_profile_svc.get_user_profile.return_value = {
            "id": "u1",
            "email": "admin@votewise.ai",
        }  # default is empty

        with patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", "admin@votewise.ai"):
            with app.test_client() as client:
                res = client.get("/admin")
                assert res.status_code == 200
                res = client.get("/voter")
                assert res.status_code == 200

        # Voter trying to access admin
        mock_identity.return_value = {"user_id": "u2", "role": "voter"}
        with app.test_client() as client:
            res = client.get("/admin")
            assert res.status_code == 403
            res = client.get("/voter")
            assert res.status_code == 200

    def test_generate_tokens(self, app):
        with app.app_context():
            tokens = generate_tokens("u1", "admin")
            assert "access_token" in tokens
            assert "refresh_token" in tokens

    @patch("middleware.auth_middleware.firebase_auth_service")
    def test_verify_firebase_token(self, mock_firebase):
        mock_firebase.verify_id_token.return_value = {"uid": "u1"}
        assert verify_firebase_token("token") == {"uid": "u1"}
