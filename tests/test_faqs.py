"""
Tests for FAQ routes.
"""

import json
from unittest.mock import patch


class TestFAQRoutes:
    """Test FAQ API endpoints."""

    def test_get_faqs(self, client):
        """Test getting all FAQs."""
        with patch("services.faq_service.FAQService.get_all_paginated") as mock_get_all:
            mock_get_all.return_value = (
                [
                    {"id": "1", "question": "Q1", "answer": "A1"},
                    {"id": "2", "question": "Q2", "answer": "A2"},
                ],
                2
            )

            response = client.get("/api/faqs")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert len(data["data"]["faqs"]) == 2

    def test_get_faqs_by_category(self, client):
        """Test getting FAQs filtered by category."""
        with patch("services.faq_service.FAQService.get_all_paginated") as mock_get_all:
            mock_get_all.return_value = (
                [{"id": "1", "question": "Q1", "answer": "A1", "category": "eligibility"}],
                1
            )

            response = client.get("/api/faqs?category=eligibility")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True

    def test_get_faqs_by_language(self, client):
        """Test getting FAQs filtered by language."""
        with patch("services.faq_service.FAQService.get_all_paginated") as mock_get_all:
            mock_get_all.return_value = ([], 0)

            response = client.get("/api/faqs?language=hi")
            assert response.status_code == 200
            mock_get_all.assert_called_with(category=None, language="hi", page=1, limit=20)

    def test_get_single_faq(self, client):
        """Test getting a single FAQ by ID."""
        with patch("services.faq_service.FAQService.get_by_id") as mock_get:
            mock_get.return_value = {"id": "faq-1", "question": "Q1", "answer": "A1"}

            response = client.get("/api/faqs/faq-1")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["data"]["id"] == "faq-1"

    def test_get_nonexistent_faq(self, client):
        """Test getting a FAQ that doesn't exist."""
        with patch("services.faq_service.FAQService.get_by_id") as mock_get:
            mock_get.return_value = None

            response = client.get("/api/faqs/nonexistent")
            assert response.status_code == 404

    def test_create_faq_no_auth(self, client):
        """Test creating FAQ without authentication."""
        response = client.post(
            "/api/faqs",
            data=json.dumps({"question": "Q1", "answer": "A1"}),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_create_faq_missing_fields(self, client, auth_headers):
        """Test creating FAQ with missing required fields."""
        with patch("middleware.auth_middleware.verify_jwt_in_request"):
            response = client.post(
                "/api/faqs",
                data=json.dumps({"question": "Q1"}),
                headers=auth_headers,
                content_type="application/json",
            )
            assert response.status_code == 401

    def test_create_faq_as_admin(self, client, auth_headers):
        """Test creating FAQ as admin."""
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch("services.faq_service.FAQService.create") as mock_create,
            patch("middleware.auth_middleware.user_profile_service.get_user_profile") as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ""),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ""}
            mock_create.return_value = {
                "id": "new-faq",
                "question": "Q1",
                "answer": "A1",
            }

            response = client.post(
                "/api/faqs",
                data=json.dumps({"question": "Q1", "answer": "A1"}),
                headers=auth_headers,
                content_type="application/json",
            )

            assert response.status_code == 201

    def test_create_faq_as_voter(self, client, auth_headers):
        """Test creating FAQ as voter (should fail)."""
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
        ):
            mock_identity.return_value = {"user_id": "voter-id", "role": "voter"}

            response = client.post(
                "/api/faqs",
                data=json.dumps({"question": "Q1", "answer": "A1"}),
                headers=auth_headers,
                content_type="application/json",
            )

            assert response.status_code == 403

    def test_update_faq_as_admin(self, client, auth_headers):
        """Test updating FAQ as admin."""
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch("services.faq_service.FAQService.update") as mock_update,
            patch("middleware.auth_middleware.user_profile_service.get_user_profile") as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ""),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ""}
            mock_update.return_value = {
                "id": "faq-1",
                "question": "Updated",
                "answer": "A1",
            }

            response = client.put(
                "/api/faqs/faq-1",
                data=json.dumps({"question": "Updated"}),
                headers=auth_headers,
                content_type="application/json",
            )

            assert response.status_code == 200

    def test_delete_faq_as_admin(self, client, auth_headers):
        """Test deleting FAQ as admin."""
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch("services.faq_service.FAQService.delete") as mock_delete,
            patch("middleware.auth_middleware.user_profile_service.get_user_profile") as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ""),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ""}
            mock_delete.return_value = True

            response = client.delete("/api/faqs/faq-1", headers=auth_headers)

            assert response.status_code == 200

    def test_delete_nonexistent_faq(self, client, auth_headers):
        """Test deleting a FAQ that doesn't exist."""
        with (
            patch("middleware.auth_middleware.verify_jwt_in_request"),
            patch("middleware.auth_middleware.get_jwt_identity") as mock_identity,
            patch("services.faq_service.FAQService.delete") as mock_delete,
            patch("middleware.auth_middleware.user_profile_service.get_user_profile") as mock_profile,
            patch("middleware.auth_middleware.ALLOWED_ADMIN_EMAIL", ""),
        ):
            mock_identity.return_value = {"user_id": "admin-id", "role": "admin"}
            mock_profile.return_value = {"email": ""}
            mock_delete.return_value = False

            response = client.delete("/api/faqs/nonexistent", headers=auth_headers)

            assert response.status_code == 404


class TestFAQSecurity:
    """Test FAQ security."""

    def test_faq_ids_sanitized(self, client):
        """Test that FAQ IDs are properly validated."""
        response = client.get("/api/faqs/../../../etc/passwd")
        assert response.status_code in [400, 404]

    def test_faq_content_not_escaped_properly(self, client):
        """Test that FAQ content is handled safely."""
        with patch("services.faq_service.FAQService.get_by_id") as mock_get:
            mock_get.return_value = {
                "id": "1",
                "question": "<script>alert('xss')</script>",
                "answer": "Safe answer",
            }

            response = client.get("/api/faqs/1")
            assert response.status_code == 200
