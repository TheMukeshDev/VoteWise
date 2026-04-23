"""
Tests for API smoke tests across all pages.
"""

import pytest
import json


class TestHomepage:
    """Smoke tests for homepage."""

    def test_homepage_loads(self, client):
        """Test homepage loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_homepage_has_title(self, client):
        """Test homepage has correct title."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"VoteWise" in response.data

    def test_homepage_has_navbar(self, client):
        """Test homepage has navbar elements."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"navbar" in response.data.lower() or b"nav" in response.data.lower()

    def test_homepage_has_hero(self, client):
        """Test homepage has hero section."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"hero" in response.data.lower() or b"Understand" in response.data


class TestVoterDashboard:
    """Smoke tests for voter dashboard."""

    def test_dashboard_loads(self, client):
        """Test voter dashboard loads successfully."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_dashboard_has_sidebar(self, client):
        """Test dashboard has sidebar."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"sidebar" in response.data.lower()

    def test_dashboard_has_quick_actions(self, client):
        """Test dashboard has quick action cards."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"Register" in response.data or b"Quick" in response.data


class TestAdminDashboard:
    """Smoke tests for admin dashboard."""

    def test_admin_loads(self, client):
        """Test admin dashboard loads successfully."""
        response = client.get("/admin")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_admin_has_stats(self, client):
        """Test admin has stats section."""
        response = client.get("/admin")
        assert response.status_code == 200
        assert b"Users" in response.data or b"Stats" in response.data


class TestAuthPages:
    """Smoke tests for authentication pages."""

    def test_login_page_loads(self, client):
        """Test login page loads."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data
        assert b"Sign In" in response.data or b"Login" in response.data

    def test_signup_page_loads(self, client):
        """Test signup page loads."""
        response = client.get("/signup")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data
        assert b"Sign Up" in response.data or b"Create" in response.data

    def test_signup_has_form(self, client):
        """Test signup page has registration form."""
        response = client.get("/signup")
        assert response.status_code == 200
        assert b"email" in response.data.lower()


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_endpoint(self, client):
        """Test health check returns proper format."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data or "version" in data


class TestErrorHandling:
    """Test error handling across pages."""

    def test_404_page(self, client):
        """Test 404 page handling."""
        response = client.get("/nonexistent-page-xyz")
        assert response.status_code == 404

    def test_api_404_format(self, client):
        """Test API returns proper error format."""
        response = client.get("/api/nonexistent-endpoint-xyz")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False
